from cltl.factual_question_processing.wikipedia_responder import WikipediaResponder

replier = WikipediaResponder()

reply = replier.factual_respond("can you search pineapple")
print(reply)
