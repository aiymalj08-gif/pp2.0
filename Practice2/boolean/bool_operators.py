# Boolean operators: and, or, not

has_id = True
has_ticket = False

can_enter = has_id and has_ticket
print("Can enter:", can_enter)

has_invitation = True
can_enter_event = has_ticket or has_invitation
print("Can enter event:", can_enter_event)

is_raining = False
print("Is not raining:", not is_raining)
