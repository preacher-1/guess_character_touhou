import random
import time
import re


class GuessCharacter:
    def __init__(self):
        self.to_avoid = None  # 想要筛除的曲目
        self.ques_guessed = []  # Guessed:a,e,s
        self.ques = []  # 1、Virtual to LIVE
        self.ques_template = []  # 1、Virtual to LIVE -> 1、*****a* ** ***E
        self.ques_dict = dict()  # {"a":[]}
        self.unsolved = 0  # 待解决题目数
        self.solved = set()  # 已解决的题目序号

    def set(self) -> None:
        print("请输入题目数：")
        while True:
            try:
                self.unsolved = int(input())
                if self.unsolved <= 0:
                    raise Exception
                break
            except:
                print("输入不合法，请重新输入！")
        with open("characters.txt", mode="r", encoding="utf-8") as f:
            source = [line.strip() for line in f.readlines()]
        self.ques.extend(random.sample(source, self.unsolved))
        self.shuffle()
        # 字符表和题目模板
        for i in range(self.unsolved):
            self.ques_template.append(re.sub(r"\S", "*", self.ques[i]))
            for j in range(len(self.ques[i])):
                ch = self.ques[i][j]
                if ch != " ":
                    if ch in self.ques_dict:
                        self.ques_dict[ch].append((i, j))
                    else:
                        self.ques_dict[ch] = [(i, j)]

    def add_ques(self, src, num) -> list[str] | None:
        if num == 0:
            return None
        # 设置曲目库
        with open(
            f"./songs/{self.src_dic[src]}_song_names.txt", mode="r", encoding="utf-8"
        ) as f:
            source = f.readlines()
        source = list(map(lambda s: re.split(r"\t+", s.strip())[1], source))

        # 随机抽歌
        self.ques.extend(random.sample(source, num))
        self.unsolved += num

        # 题目修订
        def check_input(s):
            input_valid = True
            for nb in s:
                try:
                    nb = int(nb)
                    if nb < 0 or nb > self.unsolved:
                        raise Exception
                except:
                    input_valid = False
                    break
            return input_valid

        self.to_avoid = set()
        while True:
            self.print_ques()
            to_replace = input("输入需要替换的曲目序号（无需替换直接回车）：\n").split(
                " "
            )
            if not to_replace[0]:  # 输入回车退出循环
                break
            if not check_input(to_replace):  # 输入不合法继续循环
                print("输入不合法!\n----------")
                continue
            to_replace = list(map(int, to_replace))

            for i in to_replace:
                self.to_avoid.add(self.ques[i - 1])
            for i in to_replace:
                self.ques[i - 1] = random.choice(list(set(source) - self.to_avoid))

        return self.ques

    def guess_char(self, char) -> bool:
        # 直接输入回车，char为空，返回上一级
        if not char:
            return False

        if char not in self.ques_guessed:
            self.ques_guessed.append(char)
        if char.isalpha():
            chs = (char.lower(), char.upper())
            if not any(
                map(lambda x: x in self.ques_dict, chs)
            ):  # 如果大小写都不在表中，返回False
                print("字符不存在！")
                return False
            if chs[0] in self.ques_dict:
                for val in self.ques_dict[chs[0]]:
                    i, j = val
                    temp = list(self.ques_template[i])
                    temp[j] = chs[0]
                    self.ques_template[i] = "".join(temp)
                del self.ques_dict[chs[0]]

            if chs[1] in self.ques_dict:
                for val in self.ques_dict[chs[1]]:
                    i, j = val
                    temp = list(self.ques_template[i])
                    temp[j] = chs[1]
                    self.ques_template[i] = "".join(temp)
                del self.ques_dict[chs[1]]
            return True
        else:
            if char in self.ques_dict:
                for val in self.ques_dict[char]:
                    i, j = val
                    temp = list(self.ques_template[i])
                    temp[j] = char
                    self.ques_template[i] = "".join(temp)
                del self.ques_dict[char]
                return True
        return False

    def print_template(self) -> None:
        temp = "Guessed: " + ",".join(self.ques_guessed)
        for i, ques in enumerate(self.ques_template, start=1):
            temp += f"\n{i}.\t{ques}"
        print(temp)

    def print_ques(self) -> None:
        for i, ques in enumerate(self.ques, start=1):
            print(f"{i}、\t{ques}")

    def show(self, num: int) -> bool:
        if num > len(self.ques) or num < 1:
            print("输入不合法!")
            return False
        if num in self.solved:
            print("重复输入!")
            return False
        self.ques_template[num - 1] = self.ques[num - 1]
        self.unsolved -= 1
        self.solved.add(num)
        return True

    def shuffle(self) -> None:
        seed = time.time()
        random.Random(seed).shuffle(self.ques)

    def play(self):
        self.set()
        self.print_template()
        while self.unsolved > 0:
            print("----------\n开字母1/揭晓答案2/结束3:")
            opt, content = input().strip().split(" ")
            if opt == "1":
                # print("输入单个字符:")
                self.guess_char(content)
                self.print_template()

            elif opt == "2":
                print("输入序号:")
                # idx = input()
                try:
                    idx = int(content)
                except:
                    print("输入不合法！")
                else:
                    self.show(idx)
                    self.print_template()
            elif opt == "3":
                print("\nGame over")
                break
            else:
                print("输入不合法！")

        print("\nGame over")


guess = GuessCharacter()
guess.play()
