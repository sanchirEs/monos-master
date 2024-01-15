""" setup xp """
from receptmanager.models import ReceptManager
from campaign.models import CampaignData

def reconfigure_xp():
    """ configure xp """

    managers = ReceptManager.objects.all()

    for manager in managers:

        manager.rx_xp = 0

        manager.rx_weekly_xp = 0

        manager.rx_monthly_xp = 0

        manager.rx_xp_on_comment = 0

        manager.rx_xp_on_advice = 0

        manager.rx_xp_on_test = 0

        manager.rx_xp_on_like = 0

        manager.save()

        CampaignData.objects.filter(manager=manager).delete()
