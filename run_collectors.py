import asyncio
from backend.ingestion import ALL_COLLECTORS


async def main():
    for collector_class in ALL_COLLECTORS:
        collector = collector_class()
        result = await collector.collect()
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
