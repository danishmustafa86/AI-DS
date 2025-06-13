from agents import Runner, RunContextWrapper # type: ignore
from airline_agent_new import (
    faq_agent,
    seat_agent,
    status_agent,
    baggage_agent,
    boarding_pass_agent,
    loyalty_agent,
    rebooking_agent,
    translator_agent,
    airport_info_agent,
    invoice_agent,
    meal_agent,
    AirlineAgentContext,
)


async def run_agent(message: str, user_id: str = None, email: str = None) -> str:
    runner = Runner(
        agents=[
            faq_agent,
            seat_agent,
            status_agent,
            baggage_agent,
            boarding_pass_agent,
            loyalty_agent,
            rebooking_agent,
            translator_agent,
            airport_info_agent,
            invoice_agent,
            meal_agent,
        ],
        context=AirlineAgentContext(user_id=user_id, email=email),
    )

    output = await runner.run([message])
    return output.pretty_print()
