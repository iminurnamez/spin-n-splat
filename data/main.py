from . import prepare,tools
from .states import drawing

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"DRAW": drawing.Drawing()}
    controller.setup_states(states, "DRAW")
    controller.main()
