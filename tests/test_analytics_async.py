import responses

from tests.support import with_resource, with_fixture, characters

from twitter_ads.account import Account
from twitter_ads.client import Client
from twitter_ads.campaign import Campaign
from twitter_ads.resource import Analytics
from twitter_ads.enum import METRIC_GROUP, GRANULARITY
from twitter_ads import API_VERSION


@responses.activate
def test_analytics_async():
    responses.add(responses.GET,
                  with_resource('/' + API_VERSION + '/accounts/2iqph'),
                  body=with_fixture('accounts_load'),
                  content_type='application/json')

    responses.add(responses.POST,
                  with_resource('/' + API_VERSION + '/stats/jobs/accounts/2iqph'),
                  body=with_fixture('analytics_async_post'),
                  content_type='application/json')

    responses.add(responses.GET,
                  with_resource('/' + API_VERSION + '/stats/jobs/accounts/2iqph'),
                  body=with_fixture('analytics_async_get'),
                  content_type='application/json')

    client = Client(
        characters(40),
        characters(40),
        characters(40),
        characters(40)
    )

    account = Account.load(client, '2iqph')

    ids = ['aaaa']
    metric_groups = [METRIC_GROUP.ENGAGEMENT]
    stats = Campaign.queue_async_stats_job(
        account,
        ids,
        metric_groups,
        granularity=GRANULARITY.TOTAL
    )

    # test POST request response - queue_async_stats_job()
    assert 'granularity=TOTAL' in responses.calls[1].request.url
    assert stats is not None
    assert isinstance(stats, dict)
    assert stats['entity_ids'] == ids

    # call async_stats_job_result() through Campaign class (inheritance)
    job_id = stats['id_str']
    job_result = Campaign.async_stats_job_result(
        account,
        [job_id]).first

    assert job_result is not None
    assert isinstance(job_result, dict)
    assert job_result['url'] == 'https://ton.twimg.com/advertiser-api-async-analytics/stats.json.gz'

    # call async_stats_job_result() from Analytics class directly
    job_result = Analytics.async_stats_job_result(
        account,
        [job_id]).first

    assert job_result is not None
    assert isinstance(job_result, dict)
    assert job_result['url'] == 'https://ton.twimg.com/advertiser-api-async-analytics/stats.json.gz'
