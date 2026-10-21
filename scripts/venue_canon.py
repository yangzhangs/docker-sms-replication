# -*- coding: utf-8 -*-
"""场馆名归一化（v2 图表/统计共用）。
规则顺序敏感：先特化（ESEM/TOSEM/SCAM/SANER截断等），后泛化。
截断串兜底：80字符导入截断场景下用缩写 token 兜底匹配。
"""
import re


def canon(v):
    vl = v.lower()
    rules = [
        ('source code analysis and mani', 'SCAM'),
        ('symposium on empirical software', 'ESEM'),
        ('empirical software engineering and measurement', 'ESEM'),
        ('empirical software engineering', 'ESE'),
        ('evaluation and assessment in software engineering', 'EASE'),
        ('evaluation and assessment', 'EASE'),
        ('transactions on software engineering and methodology', 'TOSEM'),
        ('transactions on software engineering', 'TSE'),
        ('international conference on software engineering', 'ICSE'),
        ('mining software repositories', 'MSR'),
        ('esec/fse', 'FSE'), ('joint european software engineering', 'FSE'),
        ('foundations of software engineering', 'FSE'), ('sigsoft', 'FSE'),
        ('software testing and analysis', 'ISSTA'),
        ('software maintenance and evolution', 'ICSME'),
        ('ieee access', 'IEEE Access'),
        ('automated software engineering', 'ASE'),
        ('software analysis, evolution and reengin', 'SANER'),
        ('journal of systems and software', 'JSS'),
        ('information and software technology', 'IST'),
        ('software and system processes', 'ICSSP'),
        ('software and systems reuse', 'ICSRE'),
        ('asia-pacific software engineering', 'APSEC'),
        ('computers, software, and applications', 'COMPSAC'),
        ('parallel and distributed systems', 'ICPADS'),
        ('service-oriented computing', 'ICSOC'),
        ('web services', 'ICWS'),
        ('service-oriented system engineering', 'SOSE'),
        ('cloud engineering', 'IC2E'),
        ('joint cloud computing', 'JCC'),
        ('reproducibility and replicability', 'REP'),
        ('software reliability engineering', 'ISSRE'),
        ('cluster computing', 'CLUSTER'),
        ('program comprehension', 'ICPC'),
        ('internetware', 'Internetware'),
        ('softwarex', 'SoftwareX'),
        ('journal of computer science and technology', 'JCST'),
        ('ieice transactions', 'IEICE Trans. Inf. Syst.'),
        ('software: practice and experience', 'SPE'),
        ('science of computer programming', 'SCP'),
        ('software and systems modeling', 'SoSyM'),
        ('applied sciences', 'Applied Sciences'),
        ('international conference on intelligent computing', 'ICIC'),
        ('ecsa', 'ECSA'),
        ('ict4sd', 'ICT4SD'),
        ('networking, intelligent systems', 'NISS'),
        ('global conference on information technology', 'GCITCN'),
    ]
    for pat, short in rules:
        if pat in vl:
            return short
    # 兜底：80字符截断串里的缩写 token（如 "FSE 2025 (PACMSE)"、"SANER 2019"、"ICSE 2026"）
    tok = {'fse': 'FSE', 'issta': 'ISSTA', 'icse': 'ICSE', 'saner': 'SANER',
           'msr': 'MSR', 'icsme': 'ICSME', 'compsac': 'COMPSAC'}
    for t, short in tok.items():
        if re.search(r'(?<![a-z])' + t + r'(?![a-z])', vl):
            return short
    return v  # 原样
