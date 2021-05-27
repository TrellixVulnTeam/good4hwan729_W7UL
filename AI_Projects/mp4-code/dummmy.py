import math
def viterbi_3(train, test):
    tagfreq = {}        #Count occurences of tags
    tagpairfreq = {}    #Count occurences of tag sequence
    tagword = {}        #Count occurences of words for each tag
    wordlist = {}
    transp = {}
    initp = {}
    emisp = {}
    notemisp = {}
    hapax = {}
    hapax_output = {}
    hapax_dict = {}
    hapax_tot = 0
    laplace = 0.0001    #smoothing parameter
    vit = {}            #will store the max
    bit = {}            #pointer to previous tag
    output = []
    suffixes = ["ly", "s", "ing", "ed", "er", "ion" "s'"] #NEW FOR PART 4
    prefixes = ["un", "re", "ir", "dis"]

#STEP 1 : Count occurrences of tags, tag pairs, tag/word pairs.
    for sentence in train:
        if sentence[1][1] not in initp: #store occurences of tag in start of a sentence
            initp[sentence[1][1]] = 1
        else:
            initp[sentence[1][1]] += 1
        for word in sentence:
            if word[1] not in tagfreq:  #store the occurences of each tag into a dict
                tagfreq[word[1]] = 1
            else:
                tagfreq[word[1]] += 1

            if word[1] not in tagword:  #store the occurences of each word for tag into a dict
                wordfreq = {}
                wordfreq[word[0]] = 1
                tagword[word[1]] = wordfreq

            else:
                if word[0] not in tagword[word[1]]:
                    tagword[word[1]][word[0]] = 1
                else:
                    tagword[word[1]][word[0]] += 1
            if word[0] not in wordlist:
                wordlist[word[0]] = 1
            else:
                wordlist[word[0]] += 1

        for i in range(len(sentence)-1):    #store the occurences of each tag sequence into a dict
            if (sentence[i][1], sentence[i+1][1]) not in tagpairfreq:
                tagpairfreq[(sentence[i][1], sentence[i+1][1])] = 1
            else:
                tagpairfreq[(sentence[i][1], sentence[i+1][1])] += 1

    for tag, words in tagword.items():
        for word, wordval in words.items():
            if wordval == 1:
                if tag not in hapax:
                    hapax[tag] = 1
                    hapax_tot += 1
                else:
                    hapax[tag] += 1
                    hapax_tot += 1
                hapax_output[word] = tag
                if tag not in hapax_dict:
                    temp_dict = {}
                    temp_dict[word] = 1
                    hapax_dict[tag] = temp_dict
                else:
                    if word not in hapax_dict[tag]:
                        hapax_dict[tag][word] = 1
                    else:
                        hapax_dict[tag][word] += 1

    #print(hapax_dict["NOUN"])
    #NEW FOR PART 4
    for i in hapax_output:
        for suff in suffixes:
            thing = "X-" + suff
            if i.endswith(suff) and thing not in tagword[hapax_output[i]] and hapax_output[i] != "X":
                tagword[hapax_output[i]][thing] = 1
            elif i.endswith(suff) and thing in tagword[hapax_output[i]] and hapax_output[i] != "X":
                tagword[hapax_output[i]][thing] += 1
        for pref in prefixes:
            thing = "X-" + pref
            if i.startswith(pref) and thing not in tagword[hapax_output[i]] and hapax_output[i] != "X":
                tagword[hapax_output[i]][thing] = 1
            elif i.startswith(pref) and thing in tagword[hapax_output[i]] and hapax_output[i] != "X":
                tagword[hapax_output[i]][thing] += 1

#STEP 2 : Compute smoothed probabilities
    for i in initp:       #Precompute Initial Probabilities
        initp[i] = math.log(initp[i] / len(train))

    for tagb in tagfreq:             #Precompute Transition probabilities
        for taga in tagfreq:
            count = 0
            for j in tagpairfreq:
                if j[0] == taga:
                    count += 1
            if (taga, tagb) not in tagpairfreq:
                transp[(taga,tagb)] = math.log(laplace / (tagfreq[tagb] + laplace*(count + 1)))
            else:
                transp[(taga,tagb)] = math.log((tagpairfreq[(taga, tagb)] + laplace) / (tagfreq[tagb] + laplace*(count + 1)))

    for sentence in train:
        for word in sentence:
            if (word[0], word[1]) not in emisp:
                if word[1] in hapax:
                    emisp[(word[0], word[1])] = math.log((tagword[word[1]][word[0]] + (laplace*hapax[word[1]]/hapax_tot)) / (tagfreq[word[1]] + (laplace*hapax[word[1]]/hapax_tot)*(len(tagword[word[1]])+ 1)))
                else:
                    emisp[(word[0], word[1])] = math.log((tagword[word[1]][word[0]] + (laplace/hapax_tot)) / (tagfreq[word[1]] + (laplace/hapax_tot)*(len(tagword[word[1]])+ 1)))

    for tag in tagfreq:
        if tag not in hapax:
            notemisp[tag] = math.log((laplace/hapax_tot) / (tagfreq[tag] + (laplace/hapax_tot)*(len(tagword[tag])+ 1)))
        else:
            notemisp[tag] = math.log((laplace*hapax[tag]/hapax_tot) / (tagfreq[tag] + (laplace*hapax[tag]/hapax_tot)*(len(tagword[tag])+ 1)))
        #NEW FOR PART 4
        for suff in suffixes:
            thing = "X-" + suff
            if thing in tagword[tag]:
                emisp[(thing,tag)] = math.log((tagword[tag][thing] + (laplace*hapax[tag]/hapax_tot)) / (tagfreq[tag] + (laplace*hapax[tag]/hapax_tot)*(len(tagword[tag])+ 1)))
        for pref in prefixes:
            thing = "X-" + pref
            if thing in tagword[tag]:
                emisp[(thing,tag)] = math.log((tagword[tag][thing] + (laplace*hapax[tag]/hapax_tot)) / (tagfreq[tag] + (laplace*hapax[tag]/hapax_tot)*(len(tagword[tag])+ 1)))

    #print(emisp[("X-ly", "NOUN")])
    #print(emisp[("X-ly", "VERB")])
    #print(emisp[("X-ly", "ADJ")])
    for sentence in test:               #Compute probabilities and construct the trellis
        temp = []
        for i in range(1,len(sentence)):
            currword = sentence[i]
            for tagb in tagfreq:
                maxdict = {}            #store sum of log for each tag

                if currword in tagword[tagb]:
                    emp = emisp[(currword, tagb)]
                else:
                    #if currword not in wordlist:
                    #NEW FOR PART 4
                    for suff in suffixes:
                        thing = "X-" + suff
                        if currword.endswith(suff) and thing in tagword[tagb]:
                            #print(currword, suff, tagb, emisp[(thing, tagb)])
                            #print(emisp[(thing, tagb)])
                            emp = emisp[(thing, tagb)]
                        else:
                            emp = notemisp[tagb]
                    # for pref in prefixes:
                        # thing = "X-" + pref
                        # if currword.startswith(pref) and thing in tagword[tagb]:
                            #print(suff, tagb)
                            #print(emisp[(thing, tagb)])
                            # emp = emisp[(thing, tagb)]
                        # else:

                    #else:
                        #emp = notemisp[tagb]

                for taga in tagfreq:
                    sum = emp

                    #STEP 3: Take the log of each probability
                    if i == 1 and tagb in initp:
                        sum += initp[tagb]
                    elif i != 1:
                        sum += vit[(i-1,taga)]
                    sum += transp[(taga,tagb)]

                    maxdict[taga] = sum

                #STEP 4 : Construct the trellis.
                vit[(i,tagb)] = max(maxdict.values())
                bit[(i,tagb)] = max(maxdict, key=maxdict.get)

        #STEP 5: Return the best path through the trellis.
        n = len(sentence)-1
        maximum = -9999999999
        for tag in tagfreq:
            if vit[(n,tag)] > maximum:
                maximum = vit[(n,tag)]
                tagidx = tag
        temp.append((sentence[n], tagidx))
        while n > 1:
            temp.append((sentence[n-1], bit[(n, tagidx)]))
            tagidx = bit[(n, tagidx)]
            n = n-1

        temp.append((sentence[0], 'START'))
        output.append(temp[::-1])

    return output
