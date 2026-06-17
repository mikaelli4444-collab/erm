from payments.payments_models import Moduls, Moduls_Companies, Subscription

def add_module(session, company_id: int, module_id: int):

    exists = session.query(Moduls_Companies).filter(Moduls_Companies.company_id == company_id,Moduls_Companies.modul_id == module_id).first()

    if exists:
        return exists

    relation = Moduls_Companies(company_id=company_id,modul_id=module_id)

    session.add(relation)
    session.commit()
    session.refresh(relation)

    return relation


def remove_module(session, company_id: int, module_id: int):

    relation = session.query(Moduls_Companies).filter(Moduls_Companies.company_id == company_id,Moduls_Companies.modul_id == module_id).first()

    if not relation:
        return False

    session.delete(relation)
    session.commit()

    return True


def assign_modules(session, company_id: int, module_ids: list[int]):

    for module_id in module_ids:

        add_module(
            session,
            company_id,
            module_id
        )


def get_company_modules(session, company_id: int):

    return session.query(Moduls).join(Moduls_Companies,Moduls.id == Moduls_Companies.modul_id).filter(Moduls_Companies.company_id == company_id).all()


def has_module(session, company_id: int, slug: str):

    module = session.query(Moduls).join(Moduls_Companies,Moduls.id == Moduls_Companies.modul_id).filter(Moduls_Companies.company_id == company_id,Moduls.slug == slug).first()

    return module is not None


def calculate_amount(session, company_id: int):

    modules = get_company_modules(session, company_id)

    return sum(
        module.price
        for module in modules
    )


def update_subscription_amount(session, company_id: int):

    subscription = session.query(Subscription).filter(Subscription.company_id == company_id).first()

    if not subscription:
        return None

    subscription.amount = calculate_amount(session, company_id)

    session.commit()
    session.refresh(subscription)

    return subscription


def add_module_to_company(session, company_id: int, module_id: int):

    add_module(session, company_id, module_id)

    subscription = update_subscription_amount(session, company_id)

    #sync_abacatepay(subscription) para futuro, ahi ya actualizo el abacatepay aqui mismo

    return subscription


def remove_module_from_company(session, company_id: int,module_id: int):

    remove_module(session, company_id, module_id)

    subscription = update_subscription_amount(session, company_id)


    #sync_abacatepay(subscription) para futuro, ahi ya actualizo el abacatepay aqui mismo

    return subscription