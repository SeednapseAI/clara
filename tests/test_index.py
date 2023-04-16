from icecream import ic

from clara.chat import ChatHistory


class TestChatHistory:
    def test_create(self):
        history = ChatHistory(length_limit=3333)
        assert history.history == []
        assert history.length_limit == 3333

    def test_append(self):
        history = ChatHistory()

        history.append(("How are you?", "I'm fine!"))
        history.append(("Nice! What's your name?", "I'm Clara."))
        ic(history.history)
        assert history.history == [
            ("How are you?", "I'm fine!"),
            ("Nice! What's your name?", "I'm Clara."),
        ]

    def test_append_with_limit(self):
        history = ChatHistory(length_limit=200)

        history.append(["How are you?", "I'm fine!"])
        history.append(
            (
                "Tell me something.",
                "Sure! Did you know that honey never spoils? Archaeologists have found "
                "pots of honey in ancient Egyptian tombs that are over 3,000 years old "
                "and still perfectly edible. Honey has natural preservatives like low "
                "water content and high acidity, which make it difficult for bacteria "
                "and microorganisms to grow. As long as it is stored in a sealed "
                "container, honey can last indefinitely.",
            )
        )
        history.append(
            (
                "Interesting! Tell me another thing, please.",
                "Of course! Did you know that the speed of light is approximately "
                "299,792 kilometers per second (186,282 miles per second) in a vacuum? "
                "This incredible speed makes light the fastest thing in the universe. To "
                "put it into perspective, if you could travel at the speed of light, you "
                "could circle Earth's equator about 7.5 times in just one second! This "
                "fundamental constant of nature, known as 'c', plays a crucial role in "
                "various scientific theories, most notably in Albert Einstein's theory "
                "of relativity.",
            )
        )
        ic(history.history)
        assert history.history == [
            (
                "Interesting! Tell me another thing, please.",
                "Of course! Did you know that the speed of light is approximately "
                "299,792 kilometers per second (186,282 miles per second) in a vacuum? "
                "This incredible speed makes light the fastest thing in the universe. To "
                "put it into perspective, if you could travel at the speed of light, you "
                "could circle Earth's equator about 7.5 times in just one second! This "
                "fundamental constant of nature, known as 'c', plays a crucial role in "
                "various scientific theories, most notably in Albert Einstein's theory "
                "of relativity.",
            ),
        ]
