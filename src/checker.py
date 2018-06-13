import language_check as lc

tool = lc.LanguageTool('en-US')

def modify(text):
    #text='Hello , ; what is this.'

    matches = tool.check(text)
    text=lc.correct(text,matches)
    print(text)
    return text

#t="fasfaf asfasf "
#modify(t)
