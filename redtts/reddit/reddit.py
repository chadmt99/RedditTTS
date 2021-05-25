from typing import List
import praw
import random
from redtts.reddit import reddit_utils as ru


class ContentGenerator(object):
    """Content generator for selecting what content is the most relevant."""

    def __init__(self, url: str):
        """ Initialize content generator instance.

        Content generator class determines which comments and material from
        a given reddit submission is the most relevant.
        Args:
            url: The url of the specfic submission.
        """
        super(ContentGenerator, self).__init__()
        self.url = url

        # Instantiate reddit instance and query submission.
        self.reddit = ru.initialize_reddit_instance()
        self.submission = ru.get_submission_from_url(
            url=url, reddit=self.reddit
        )

    def get_curated_comment_chains(
            self, num_chains: int, min_chain_length: int,
            max_chain_length: int, min_character_limit=10,
            max_character_limit=1000) -> List[List[praw.models.Comment]]:
        """Get relevant comment chains

        Given current submission, decide which comment chains to expose. For
        now no forking in chains, comment chain encapsulates its own thread.
        Args:
            num_chains: Number of comment chains.
            min_chain_length: Minimum number of comments in each chain.
            min_character_limit: Maximum number of comments in each chain.
            max_character_limit: Maximum length a comment is allowed to be.
        Returns:
            List of list, where each nested list is composed of reddit
            comment objects.
        """
        curated_comment_chains = []

        # Iterate through the comment forest.
        comment_forest = self.submission.comments.list()
        comment_forest = [comment for comment in comment_forest if
                          isinstance(comment, praw.models.Comment)]

        # Sort the forest based on score of root comment.
        comment_forest.sort(key=lambda x: x.score, reverse=True)

        # Construct the chains.
        current_root = 0
        for chain in range(num_chains):
            # Generate a random chain length in accordance with the bounds.
            chain_length = random.randint(min_chain_length, max_chain_length)
            if chain_length == 0:
                continue

            # Find first valid root to traverse down.
            current_comment = None
            curated_comment_chains.append([])
            for i in range(current_root, len(comment_forest)):
                if (min_character_limit <= len(comment_forest[i].body)
                        <= max_character_limit):
                    current_root = i + 1
                    current_comment = comment_forest[i]
                    break

            # Complete the chain.
            if current_comment is not None:
                curated_comment_chains[chain].append(current_comment)
                # Chose a random int to make the chain length.
                for i in range(1, chain_length):
                    replies = current_comment.replies.list()
                    replies = [reply for reply in replies if
                               isinstance(reply, praw.models.Comment)]
                    replies.sort(key=lambda x: x.score, reverse=True)
                    # Find first valid comment.
                    for reply in replies:
                        if (min_character_limit <= len(reply.body)
                                <= max_character_limit):
                            curated_comment_chains[chain].append(reply)
                            current_comment = reply
                            break

        return curated_comment_chains
