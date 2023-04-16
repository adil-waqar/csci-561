from collections import deque
from copy import deepcopy
from itertools import product
import re
from typing import Deque, Dict, List


class Predicate:
    def __init__(self, name: str, neg: bool, args: List[str], sent_id: int, pred_id: int):
        self.name = name
        self.neg = neg
        self.args = args
        self.sent_id = sent_id
        self.pred_id = pred_id
        self.ground_literal = self.is_ground_literal()

    def is_ground_literal(self) -> bool:
        for i in self.args:
            if i[0].islower():
                return False
        return True

    def __str__(self):
        return ('~' if self.neg else '')+self.name+'('+','.join(self.args)+')'

    def __eq__(self, o: object) -> bool:
        if len(self.args) != len(o.args):
            return False
        if not isinstance(o, type(self)):
            return False
        if self.name != o.name:
            return False

        if self.ground_literal and o.ground_literal:
            for x, y in zip(self.args, o.args):
                if x != y:
                    return False
        for x, y in zip(self.args, o.args):
            if x[0].isupper():
                if y[0].isupper():
                    if x != y:
                        return False
            elif y[0].isupper():
                if x[0].isupper():
                    if x != y:
                        return False
        return True

    def update_id(self, id: int):
        self.pred_id = id

    def compliment_of(self, pred):
        return self.neg == (not pred.neg)

    def substitute_args(self, mapping: Dict[str, str]):
        self.args = [arg if arg not in mapping else mapping[arg]
                     for arg in self.args]
        self.ground_literal = self.is_ground_literal()


class Sentence:
    def __init__(self, preds: List[Predicate], id: int) -> None:
        self.preds = preds
        self.id = id
        self.constant = self.is_constant()
        self.ground_literal = self.is_ground_literal()

    def is_constant(self):
        return all([pred.ground_literal for pred in self.preds])

    def __str__(self):
        return '|'.join([str(pred) for pred in self.preds])

    def remove_predicate(self, pred: Predicate):
        self.preds = [p for p in self.preds if pred.pred_id != p.pred_id]
        self.constant = self.is_constant()
        self.ground_literal = self.is_ground_literal()

    def reassign_pred_ids(self):
        for idx, pred in enumerate(self.preds):
            pred.update_id(idx)

    def substitute_args(self, mapping: Dict[str, str]):
        for pred in self.preds:
            pred.substitute_args(mapping)
        self.constant = self.is_constant()
        self.ground_literal = self.is_ground_literal()

    def update_sentence_id(self, id: int):
        self.id = id
        for pred in self.preds:
            pred.sent_id = id

    def is_ground_literal(self):
        if len(self.preds) == 1 and self.constant:
            self.ground_literal = True
            return True

        self.ground_literal = False
        return False

    def is_empty(self):
        return True if len(self.preds) == 0 else False


class KB:
    def __init__(self, sentences: List[str] = []) -> None:
        self.sentences = self.populate(sentences)
        self.pp_kb()

    def inject(self, sentence: Sentence):
        self.sentences.append(sentence)

    def populate(self, sentences: List[str]) -> List[Sentence]:
        sent_list = []
        variables = set()
        for sentence in sentences:
            for v in re.findall(r'\((.*?)\)', sentence):
                for s in v.split(','):
                    if s[0].islower():
                        variables.add(s)

        for sentence_id, sentence in enumerate(sentences):
            for v in variables:
                sentence = sentence.replace('('+v, '('+v+str(sentence_id))
                sentence = sentence.replace(','+v, ','+v+str(sentence_id))

            preds = sentence.split('|')
            pred_list = []
            for pred_id, pred in enumerate(preds):
                neg = True if pred[0] == '~' else False
                pred_name = pred[1:pred.find(
                    '(')] if neg else pred[0:pred.find('(')]
                args = re.findall(r'\((.*?)\)', pred)[0].split(',')
                p = Predicate(pred_name, neg, args, sentence_id, pred_id)
                pred_list.append(p)

            sent = Sentence(pred_list, sentence_id)
            sent_list.append(sent)

        return sent_list

    def pp_kb(self):
        for sentence in self.sentences:
            print(sentence)


class Restaurant:
    def __init__(self) -> None:
        f = open('input.txt', 'r').read()
        lines = f.split('\n')
        self.query = lines[0]
        self.k = int(lines[1])
        self.kb = [x.replace(' ', '') for x in lines[2:self.k+2]]
        self.kb.append(self.negate_query())
        self.kb_to_cnf()
        self.KBase = KB(self.kb)
        self.literal_stack = self.gen_literal_stack()
        self.KDict = self.gen_k_dict()

    def to_cnf(self, clause: str) -> str:
        if "=>" in clause:
            lhs, rhs = clause.split('=>')[0], clause.split('=>')[1]
            if '&' in lhs and '|' not in lhs:
                lhs = '|'.join(
                    [x[1:] if x[0] == '~' else '~'+x for x in lhs.split('&')])
                return lhs + '|' + rhs
            elif '|' in lhs and '&' not in lhs:
                dj = []
                for l in lhs.split('|'):
                    if l[0] == '~':
                        dj.append(l[1:] + '|' + rhs)
                    else:
                        dj.append('~' + l + '|' + rhs)
                return '&'.join(dj)
            elif '|' not in lhs and '&' not in lhs:
                if lhs[0] == '~':
                    return lhs[1:] + '|' + rhs
                else:
                    return '~' + lhs + '|' + rhs
            else:
                dj = []
                for clause in lhs.split('|'):
                    preds = [pred[1:] if pred[0] ==
                             '~' else '~'+pred for pred in clause.split('&')]
                    or_preds = '|'.join(preds)
                    dj.append(or_preds + '|' + rhs)
                return '&'.join(dj)
        elif ('=>' not in clause) and ('|' in clause and '&' in clause):
            preds = []
            for c1 in clause.split('|'):
                preds.append(c1.split('&'))
            prod = list(product(*preds))
            dj = ['|'.join(tup) for tup in prod]
            return '&'.join(dj)

        else:
            return clause

    def kb_to_cnf(self):
        kb = []
        for sentence in self.kb:
            conv = self.to_cnf(sentence)
            kb.extend(conv.split('&'))
        self.kb = kb
        self.k = len(kb)

    def pp_kb(self):
        for sentence in self.kb:
            print(sentence)

    def unify(self, cl1: Predicate, cl2: Predicate):
        if cl1.name == cl2.name and cl1.compliment_of(cl2) and cl1.args == cl2.args:
            return None, {}, {}
        if cl1 != cl2:
            return False, {}, {}
        if cl1.neg == cl2.neg:
            return False, {}, {}
        if len(cl1.args) != len(cl2.args):
            return False, {}, {}
        unifier = {}
        unifier_rev = {}
        for ac1, ac2 in zip(cl1.args, cl2.args):
            a1, a2 = ac1[0], ac2[0]
            if a1.isupper() and a2.isupper():
                if ac1 != ac2:
                    return False, {}, {}
            elif a1.islower():
                if ac1 in cl2.args:
                    return False, {}, {}
                unifier[ac1] = ac2
            elif a2.islower():
                if ac2 in cl1.args:
                    return False, {}, {}
                unifier_rev[ac2] = ac1
        return True, unifier, unifier_rev

    def resolve(self):
        unified_pairs = {}
        new_clauses_map = {}

        while True:
            query = self.literal_stack.pop()
            self.literal_stack.appendleft(query)

            if query.sent_id not in unified_pairs:
                unified_pairs[query.sent_id] = []

            if query.sent_id not in new_clauses_map:
                new_clauses_map[query.sent_id] = -1

            unifications = [
                pred for pred in self.KDict[query.name] if pred.compliment_of(query)]

            new_clauses = 0
            for predicate in unifications:
                if predicate.sent_id in unified_pairs[query.sent_id]:
                    continue
                can_unify, u1, u2 = self.unify(predicate, query)

                sentence = self.KBase.sentences[predicate.sent_id]
                if can_unify or can_unify == None:
                    sentence_copy = deepcopy(sentence)
                    if can_unify:
                        sentence_copy.substitute_args(u1)
                    sentence_copy.remove_predicate(predicate)
                    if sentence_copy.is_empty():
                        print('Contradiction found: ',
                              sentence, '\t', query)
                        return True
                    sentence_copy.reassign_pred_ids()
                    sentence_copy.update_sentence_id(self.k)

                    if (self.find_by_sentence(sentence_copy)):
                        continue
                    print('unifying: ', query, '\tand\t ',
                          sentence, '\tresult\t', sentence_copy)
                    new_clauses += 1
                    self.KBase.inject(sentence_copy)
                    self.inject_k_dict(sentence_copy)
                    self.k += 1
                    sentence_copy.is_ground_literal()
                    if sentence_copy.ground_literal | len(sentence_copy.preds) == 1:
                        self.literal_stack.append(sentence_copy.preds[0])

                unified_pairs[query.sent_id].append(sentence.id)

            new_clauses_map[query.sent_id] = new_clauses
            if self.no_new_clauses(new_clauses_map):
                print("cannot infer anything else")
                return False

    def gen_literal_stack(self) -> Deque[Predicate]:
        ls = deque([])
        for sentence in self.KBase.sentences:
            if len(sentence.preds) == 1:
                ls.append(sentence.preds[0])
        return ls

    def negate_query(self):
        if self.query[0] == '~':
            return self.query[1:]
        else:
            return '~' + self.query

    def find_by_sentence(self, sentence: Sentence):
        for sent in self.KBase.sentences:
            if (str(sent) == str(sentence)):
                return True
        return False

    def gen_k_dict(self) -> Dict[str, List[Predicate]]:
        k_dict = {}
        for sentence in self.KBase.sentences:
            for pred in sentence.preds:
                if pred.name not in k_dict:
                    k_dict[pred.name] = []
                k_dict[pred.name].append(pred)
        return k_dict

    def inject_k_dict(self, sentence: Sentence):
        for pred in sentence.preds:
            self.KDict[pred.name].append(pred)

    def write_output(self, answer: bool):
        with open("output.txt", "w") as f:
            f.write(str(answer).upper())

    def no_new_clauses(self, dict: Dict[str, int]):
        return all([not dict[key] for key in dict.keys()])


if __name__ == "__main__":
    restaurant = Restaurant()
    answer = restaurant.resolve()
    restaurant.write_output(answer)
