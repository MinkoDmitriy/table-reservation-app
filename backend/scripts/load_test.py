import asyncio
import time
import argparse
import sys
from typing import List, Dict, Any
import httpx

# Color codes for nice terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'='*60}\n{title.center(60)}\n{'='*60}{RESET}")

class LoadTester:
    def __init__(self, base_url: str, concurrency: int):
        self.base_url = base_url.rstrip('/')
        self.concurrency = concurrency
        # Use a longer timeout for concurrent load
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def run_menu_test(self):
        print_header("Starting Menu Load Test (GET /api/menu_items)")
        print(f"Target URL: {self.base_url}/api/menu_items")
        print(f"Concurrency: {self.concurrency} simultaneous requests")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Send one warm-up request
            try:
                warmup = await client.get(f"{self.base_url}/api/menu_items")
                if warmup.status_code != 200:
                    print(f"{YELLOW}Warning: Warm-up request returned status {warmup.status_code}{RESET}")
            except Exception as e:
                print(f"{RED}Error: Cannot connect to backend: {e}{RESET}")
                sys.exit(1)

            print("Sending concurrent requests...")
            start_time = time.perf_counter()
            
            tasks = [client.get(f"{self.base_url}/api/menu_items") for _ in range(self.concurrency)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_duration = time.perf_counter() - start_time
            self._analyze_results(responses, total_duration)

    async def run_order_test(self):
        print_header("Starting Order Checkout Load Test (POST /api/food_baskets/{id})")
        print(f"Target URL: {self.base_url}/api/food_baskets/{{basket_id}}")
        print(f"Concurrency: {self.concurrency} unique simultaneous users")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 1. Warm-up and find active menu item
            try:
                menu_resp = await client.get(f"{self.base_url}/api/menu_items")
                if menu_resp.status_code != 200 or not menu_resp.json():
                    print(f"{RED}Error: No active menu items found. Please seed the database first.{RESET}")
                    sys.exit(1)
                menu_items = menu_resp.json()
                menu_item_id = menu_items[0]["id"]
                print(f"Using menu item ID: {menu_item_id} ('{menu_items[0]['name']}')")
            except Exception as e:
                print(f"{RED}Error connecting to backend: {e}{RESET}")
                sys.exit(1)

            # 2. Setup Phase: Register/Login users and prepare baskets
            print(f"\n{BOLD}[1/2] Setup Phase: Preparing {self.concurrency} user baskets...{RESET}")
            setup_start = time.perf_counter()
            
            # We will run user preparation in batches to avoid overwhelming the server during setup
            batch_size = 50
            user_tokens = []
            user_basket_ids = []
            
            async def prepare_single_user(index: int) -> tuple:
                username = f"load_user_{index}_{int(time.time())}"
                password = "password123"
                
                # Register user
                reg_payload = {"username": username, "password": password}
                reg_resp = await client.post(f"{self.base_url}/api/auth/register", json=reg_payload)
                
                if reg_resp.status_code == 201 or reg_resp.status_code == 200:
                    data = reg_resp.json()
                elif reg_resp.status_code == 409: # Conflict, try logging in
                    login_resp = await client.post(f"{self.base_url}/api/auth/login", json={"username": username, "password": password})
                    data = login_resp.json()
                else:
                    raise Exception(f"Failed to authenticate user {username}: {reg_resp.text}")
                
                token = data["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                # Add item to basket
                basket_payload = {"menu_item_id": menu_item_id}
                basket_resp = await client.post(
                    f"{self.base_url}/api/food_baskets", 
                    json=basket_payload, 
                    headers=headers
                )
                if basket_resp.status_code not in (200, 201):
                    raise Exception(f"Failed to add item to basket: {basket_resp.text}")
                
                basket_data = basket_resp.json()
                basket_id = basket_data["food_basket_id"]
                
                return token, basket_id

            # Execute setup tasks
            for i in range(0, self.concurrency, batch_size):
                chunk = range(i, min(i + batch_size, self.concurrency))
                chunk_tasks = [prepare_single_user(idx) for idx in chunk]
                results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
                
                for res in results:
                    if isinstance(res, Exception):
                        print(f"{RED}Setup Error: {res}{RESET}")
                    else:
                        token, basket_id = res
                        user_tokens.append(token)
                        user_basket_ids.append(basket_id)
            
            setup_duration = time.perf_counter() - setup_start
            print(f"{GREEN}Setup complete: Prepared {len(user_basket_ids)} baskets in {setup_duration:.2f} seconds.{RESET}")
            
            if len(user_basket_ids) < self.concurrency:
                print(f"{YELLOW}Warning: Only {len(user_basket_ids)} out of {self.concurrency} baskets are ready. Starting load test with prepared volume.{RESET}")
                self.concurrency = len(user_basket_ids)

            # 3. Load Phase: Concurrently order baskets
            print(f"\n{BOLD}[2/2] Load Phase: Submitting {self.concurrency} orders concurrently...{RESET}")
            
            async def submit_order(client_instance, token: str, basket_id: int):
                headers = {"Authorization": f"Bearer {token}"}
                order_payload = {
                    "order_type": "dinein",
                    "phone": "+79998887766"
                }
                
                req_start = time.perf_counter()
                try:
                    resp = await client_instance.post(
                        f"{self.base_url}/api/food_baskets/{basket_id}",
                        json=order_payload,
                        headers=headers
                    )
                    latency = time.perf_counter() - req_start
                    return resp, latency
                except Exception as exc:
                    latency = time.perf_counter() - req_start
                    return exc, latency

            # Create a separate client session for the load phase to ensure clean connection pooling
            async with httpx.AsyncClient(timeout=self.timeout) as load_client:
                load_start = time.perf_counter()
                
                load_tasks = [
                    submit_order(load_client, user_tokens[idx], user_basket_ids[idx]) 
                    for idx in range(self.concurrency)
                ]
                
                results = await asyncio.gather(*load_tasks)
                total_duration = time.perf_counter() - load_start
            
            # 4. Analyze Results
            self._analyze_order_results(results, total_duration)

    def _analyze_results(self, responses: List[Any], total_duration: float):
        success_count = 0
        error_count = 0
        latencies = []

        for resp in responses:
            if isinstance(resp, httpx.Response):
                # Count success as 200 OK
                if resp.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
                # Read latency from response headers if available, or fall back to request time
                # since gather doesn't easily give request timings unless wrapped
                # Note: httpx Response has .elapsed property (timedelta) which measures request duration
                latencies.append(resp.elapsed.total_seconds() * 1000.0) # in ms
            else:
                error_count += 1

        self._print_metrics(success_count, error_count, latencies, total_duration)

    def _analyze_order_results(self, results: List[tuple], total_duration: float):
        success_count = 0
        error_count = 0
        latencies = []

        for res, latency in results:
            latencies.append(latency * 1000.0) # convert to ms
            if isinstance(res, httpx.Response):
                if res.status_code in (200, 201):
                    success_count += 1
                else:
                    error_count += 1
                    # Log first few errors for debugging
                    if error_count <= 5:
                        print(f"{YELLOW}Request failed with status {res.status_code}: {res.text[:100]}{RESET}")
            else:
                error_count += 1
                if error_count <= 5:
                    print(f"{YELLOW}Request failed with exception: {res}{RESET}")

        self._print_metrics(success_count, error_count, latencies, total_duration)

    def _print_metrics(self, success: int, errors: int, latencies: List[float], total_duration: float):
        total_requests = success + errors
        error_rate = (errors / total_requests) * 100 if total_requests > 0 else 0
        
        print_header("Load Test Results")
        print(f"Total Requests Sent:   {total_requests}")
        print(f"Successful Responses:  {GREEN}{success}{RESET}")
        print(f"Failed Responses:      {RED if errors > 0 else GREEN}{errors} ({error_rate:.2f}%){RESET}")
        print(f"Total Test Duration:   {total_duration:.3f} seconds")
        print(f"Throughput (RPS):      {total_requests / total_duration:.2f} req/sec")
        
        if latencies:
            latencies.sort()
            avg_latency = sum(latencies) / len(latencies)
            min_latency = latencies[0]
            max_latency = latencies[-1]
            p50 = latencies[int(len(latencies) * 0.50)]
            p95 = latencies[int(len(latencies) * 0.95)]
            p99 = latencies[int(len(latencies) * 0.99)]
            
            print(f"\n{BOLD}Latency Metrics:{RESET}")
            print(f"  Min Response Time:   {min_latency:.2f} ms")
            print(f"  Average Response Time:{YELLOW}{avg_latency:.2f} ms{RESET}")
            print(f"  Max Response Time:   {max_latency:.2f} ms")
            print(f"  50th Percentile (p50): {p50:.2f} ms")
            print(f"  95th Percentile (p95): {GREEN if p95 < 100 else YELLOW}{p95:.2f} ms{RESET}")
            print(f"  99th Percentile (p99): {p99:.2f} ms")
        else:
            print(f"\n{RED}No latency data collected due to absolute failure.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FastAPI Table Reservation System Load Tester")
    parser.add_argument("mode", choices=["menu", "order"], help="Type of load test to run (menu or order)")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the FastAPI server")
    parser.add_argument("--concurrency", type=int, default=500, help="Number of simultaneous requests")
    
    args = parser.parse_args()
    
    # Run async main loop
    try:
        tester = LoadTester(args.url, args.concurrency)
        if args.mode == "menu":
            asyncio.run(tester.run_menu_test())
        elif args.mode == "order":
            asyncio.run(tester.run_order_test())
    except KeyboardInterrupt:
        print(f"\n{RED}Load test cancelled by user.{RESET}")
        sys.exit(1)
