import asyncio
import random
import aiohttp

# Global stats
total_requests = 0
success_requests = 0
failed_requests = 0

stop = False


def generate_fake_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"


async def flood_worker(session, url):
    global total_requests, success_requests, failed_requests, stop

    while not stop:
        # Dynamic load pattern
        rate = random.choice([20, 50, 100, 300, 800])
        interval = 1.0 / rate if rate > 0 else 0

        headers = {
            "X-Forwarded-For": generate_fake_ip()
        }

        try:
            async with session.get(url, headers=headers, timeout=0.5) as resp:
                total_requests += 1
                if resp.status < 500:
                    success_requests += 1
                else:
                    failed_requests += 1
        except:
            total_requests += 1
            failed_requests += 1

        if interval > 0:
            await asyncio.sleep(interval)


async def metrics_printer():
    global total_requests, success_requests, failed_requests, stop

    prev_total = 0

    while not stop:
        await asyncio.sleep(1)

        current = total_requests
        rps = current - prev_total
        prev_total = current

        print(
            f"[Stats] RPS: {rps} | Total: {total_requests} | Success: {success_requests} | Fail: {failed_requests}")


async def run_simulation(url, workers=200, duration=30):
    global stop

    connector = aiohttp.TCPConnector(limit=0)  # unlimited connections

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []

        # Start workers
        for _ in range(workers):
            tasks.append(asyncio.create_task(flood_worker(session, url)))

        # Start metrics logger
        tasks.append(asyncio.create_task(metrics_printer()))

        print(f"[Simulator] Running with {workers} workers for {duration}s...")

        await asyncio.sleep(duration)

        # Stop all workers
        stop = True

        await asyncio.gather(*tasks, return_exceptions=True)

    print("[Simulator] Finished cleanly")

if __name__ == "__main__":
    asyncio.run(run_simulation(
        "http://localhost:8000/test",   # USE LOCAL FIRST
        workers=30,
        duration=60
    ))
