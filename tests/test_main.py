import asyncio


def _make_dummy_coro():
    async def _dummy(*args, **kwargs):
        # long sleep so task remains pending until cancelled
        await asyncio.sleep(10)

    return _dummy


def test_start_and_stop_other_exchanges():
    # Import inside test to ensure environment is ready
    import main

    # Prepare dummy coroutine factories and patch functions on the main module
    dummy = _make_dummy_coro()

    main.kline_task_bybit = lambda coin, states, active: dummy()
    main.trade_task_bybit = lambda coin, states, active: dummy()
    main.trades_task_gate = lambda coin, states, active: dummy()
    main.trade_task_okx = lambda coin, states, active: dummy()

    # Ensure clean state
    main.other_exchange_tasks.clear()
    main.active_other_exchanges.clear()

    # Run the async start/stop sequence
    asyncio.run(main.start_other_exchanges("ETH"))

    # After start, tasks and active set should contain the coin
    assert "ETH" in main.other_exchange_tasks
    assert "ETH" in main.active_other_exchanges

    # Calling start again should not create duplicate entries
    asyncio.run(main.start_other_exchanges("ETH"))
    assert len(main.other_exchange_tasks["ETH"]) == 4

    # Now stop and ensure cleanup
    asyncio.run(main.stop_other_exchanges("ETH"))
    assert "ETH" not in main.other_exchange_tasks
    assert "ETH" not in main.active_other_exchanges
