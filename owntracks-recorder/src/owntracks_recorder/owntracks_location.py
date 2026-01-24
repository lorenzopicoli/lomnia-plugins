from enum import Enum


class TriggerType(str, Enum):
    """
    Trigger type
    - p ping issued randomly by background task (iOS,Android)
    - c circular region enter/leave event (iOS,Android)
    - C circular region enter/leave event for +follow regions (iOS)
    - b beacon region enter/leave event (iOS)
    - r response to a reportLocation cmd message (iOS,Android)
    - u manual publish requested by the user (iOS,Android)
    - t timer based publish in move move (iOS)
    - v updated by Settings/Privacy/Locations Services/System Services/Frequent Locations monitoring (iOS)
    """

    p = "p"
    c = "c"
    C = "C"
    b = "b"
    r = "r"
    u = "u"
    t = "t"
    v = "v"


class ConnectivityStatus(str, Enum):
    w = "w"
    o = "o"
    m = "m"
