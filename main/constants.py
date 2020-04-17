from .order import OrderState

HOT = 'hot'
COLD = 'cold'
FROZEN = 'frozen'
OVERFLOW = 'overflow'


SHELF_TO_STATE = {
    HOT: OrderState.HOT,
    COLD: OrderState.COLD,
    FROZEN: OrderState.FROZEN,
    OVERFLOW: OrderState.OVERFLOW
}

STATE_TO_SHELF = {
    OrderState.HOT: HOT,
    OrderState.COLD: COLD,
    OrderState.FROZEN: FROZEN,
    OrderState.OVERFLOW: OVERFLOW
}
