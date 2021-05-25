from typing import List
import praw
import urllib


PUSHSHIFT_URL = "https://api.pushshift.io/reddit/submission/search/?subreddit="
READ_CHAR = read_char = [
    ' ', '{', '}', '\'', '\\n', '"created_utc"', '"data"', ':', '[', ']'
]


def initialize_reddit_instance(read_only=True) -> praw.Reddit:
    """The Reddit class provides convenient access to Reddit’s API.

    Initializes onstance of this class are the gateway to interacting with
    Reddit’s API through PRAW.
    Args:
        read_only: Whether the instance is read only.
    Returns:
        A praw Reddit instance.
    """
    reddit = praw.Reddit(
        client_id='3kx2CC4EgGQGwA',
        client_secret='fCTxqT3DExG5PSsXeGLL9PIvE5A',
        user_agent='wsb_splooge_face',
        username='wsb_splooge_face',
        password='abcd1234'
    )
    reddit.read_only = read_only
    return reddit


def get_first_post_timestamp(subreddit: str) -> int:
    """Get the first posts timestamp of a particular subreddit.

    Using pushshift API access the timestamp of the first post.
    Args:
        subreddit: The subreddit to query.
    Returns:
        Unixtimestamp in seconds of the first post in the subreddit
    """
    # Getting the timestamp of first post on the subreddit.
    ps = urllib.request.urlopen(
        PUSHSHIFT_URL + subreddit + "&sort=asc&filter=created_utc&size=1"
    )
    htmltext = ps.read()
    htmltext = str(htmltext)
    htmltext = htmltext[1:]
    for c in READ_CHAR:
        htmltext = htmltext.replace(c, '')
    first_post_timestamp = int(htmltext)
    return first_post_timestamp


def get_last_post_timestamp(subreddit: str) -> int:
    """Get the last posts timestamp of a particular subreddit.

    Using pushshift API access the timestamp of the ;ast post.
    Args:
        subreddit: The subreddit to query.
    Returns:
        Unixtimestamp in seconds of the last post in the subreddit
    """
    ps = urllib.request.urlopen(
        PUSHSHIFT_URL+subreddit+"&sort=desc&filter=created_utc&size=1"
    )
    htmltext = ps.read()
    htmltext = str(htmltext)
    htmltext = htmltext[1:]
    for c in READ_CHAR:
        htmltext = htmltext.replace(c, '')
    last_post_timestamp = int(htmltext)
    return last_post_timestamp


def get_timestamps_in_range(
        subreddit: str, start_time: int,
        end_time: int, verbose=False) -> List[int]:
    """Get list of the timestamp of every thousandth post in time range.

    Given a start and end time, get a list of unix timestamps of every
    thousandth submission for the specified subreddt, due to the query
    limitations on the pushshift api.
    Args:
        subreddit: The subreddit to query.
        start_time: Unixtimestamp in seconds of the start range.
        end_time: Unixtimestamp in seconds of the end range.
        verbose: Whether to output percentage of posts queried.
    Returns:
        List of unixtimestamps.
    """
    timestamp = start_time
    timestamps = []
    while timestamp < end_time:
        timestamps.append(timestamp)
        ps = urllib.request.urlopen(
            PUSHSHIFT_URL + subreddit + "&sort=asc&filter=created_utc&after="
            + str(timestamp) + "&size=1000"
        )
        htmltext = ps.read()
        htmltext = str(htmltext)
        htmltext = htmltext[1:]
        for c in READ_CHAR:
            htmltext = htmltext.replace(c, '')
        array = htmltext.split(',')
        timestamp = int(array[-1])
        if verbose:
            percentage = (timestamp - start_time) / (
                    end_time - start_time) * 100
            print(str(round(percentage, 2)) + '%', end='\r')
    return timestamps


def get_ids_in_range(
        subreddit: str,  start_time: int,
        end_time: int, verbose=False) -> List[str]:
    """Get list of string id's in time range.

    Given a start and end time, get a list of id's of every submission for
    the specified subreddt.
    Args:
        subreddit: The subreddit to query.
        start_time: Unixtimestamp in seconds of the start range.
        end_time: Unixtimestamp in seconds of the end range.
        verbose: Whether to output percentage of posts queried.
    Returns:
        List of string id's
    """
    id_list = []
    timestamps = get_timestamps_in_range(
        subreddit, start_time, end_time, verbose=False
    )
    for timestamp in timestamps:
        ps = urllib.request.urlopen(
            PUSHSHIFT_URL + subreddit + "&sort=asc&filter=id&after="
            + str(timestamp) + "&size=1000"
        )
        htmltext = ps.read()
        htmltext = str(htmltext)
        htmltext = htmltext[1:]
        for c in [' ','{','}','\'','\\n','"id"','"data"',':','[',']','"']:
            htmltext = htmltext.replace(c, '')
        id_list = id_list + htmltext.split(',')
        if verbose:
            percentage = (timestamp - start_time) / (
                        end_time - start_time) * 100
            print(str(round(percentage, 2)) + '%', end='\r')
    return id_list


def get_submissions_from_ids(
        id_list: List[str],
        reddit: praw.Reddit, verbose=False) -> List[praw.models.Submission]:
    """Get list of praw Submission objects.

    Given an id list get submission objects associated with said id's
    Args:
        id_list: List of str id's associated with reddit posts.
        reddit: Praw Reddit instance.
        verbose: Whether to output percentage of posts queried.
    Returns:
        List of praw Submission objects.
    """
    submission_list = []
    current = 0
    total_submissions = len(id_list)
    for sub_id in id_list:
        sub = reddit.submission(id=sub_id)
        submission_list.append(sub)
        current += 1
        if verbose:
            percentage = current / total_submissions * 100
            print(str(round(percentage, 2)) + '%', end='\r')
    return submission_list


def get_submission_from_url(
        url: str, reddit: praw.Reddit) -> praw.models.Submission:
    """Get reddit submission from url.

    Given a string url get submission object associated with url.
    Args:
        url: List of str id's associated with reddit posts.
        reddit: Praw Reddit instance.
    Returns:
        praw Submission.
    """
    submission = reddit.submission(url=url)
    return submission
