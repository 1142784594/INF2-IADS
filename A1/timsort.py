# File:     timsort.py
# Author:   John Longley
# Date:     October 2022

# Template file for Inf2-IADS (2022-23) Coursework 1, Part A
# Simplified version of Timsort sorting algorithm


# Provided code for splitting list into suitable segments

# Tags for segment types:

Inc, Dec, Unsorted = +1, -1, 0


# Representing segments (L[start],...,L[end-1]):

class Segment:
    def __init__(self, start, end, tag):
        self.start = start
        self.end = end
        self.tag = tag

    def len(self):
        return self.end - self.start

    def __repr__(self):
        return ('Segment(' + str(self.start) + ',' + str(self.end) + ','
                + str(self.tag) + ')')


# Stage 1: Split entire list into Inc and Dec segments (possibly very short).

class IncDecRuns:
    def __init__(self, L, key=lambda x: x):
        self.L = L
        self.key = key
        self.m = len(L) - 1
        self.dir = Inc if key(L[1]) >= key(L[0]) else Dec
        self.i = 0  # most recent segment boundary
        self.j = 0  # position reached

    def next(self):
        # returns tuple for next segment, or None if end reached
        if self.j == self.m:
            return None
        else:
            self.i = self.j
            # scan for next change of direction
            while (self.j < self.m and
                   ((self.dir == Inc and
                     self.key(self.L[self.j]) <= self.key(self.L[self.j + 1])) or
                    (self.dir == Dec and
                     self.key(self.L[self.j]) >= self.key(self.L[self.j + 1])))):
                self.j += 1
            if self.j == self.m:
                # no change of direction at final step: include last list entry
                return Segment(self.i, self.m + 1, self.dir)
            else:
                # change of direction
                self.dir = -self.dir
                return Segment(self.i, self.j, -self.dir)

    def finished(self):
        return (self.j == self.m)


# Stage 2: Fuse consecutive short segments into longer (unsorted) ones.

# Preserve all Inc or Dec runs of at least this size:
runThreshold = 32


class FuseSegments:
    def __init__(self, IncDecRuns):
        self.IDR = IncDecRuns
        self.next1 = self.IDR.next()
        self.next2 = self.IDR.next()

    def next(self):
        if self.next2 == None:
            curr = self.next1
            self.next1 = None
            return curr
        elif self.next1.len() < runThreshold and self.next2.len() < runThreshold:
            # two short segments: fusing required
            start = self.next1.start
            # find end of run of short segments
            while self.next2.len() < runThreshold and not self.IDR.finished():
                self.next2 = self.IDR.next()
            if self.next2.len() < runThreshold:
                # next2 is last segment and is short: include in fused segment
                end = self.next2.end
                self.next1, self.next2 = None, None
            else:
                # next2 is long: exclude from fused segment
                end = self.next2.start
                self.next1 = self.next2
                self.next2 = self.IDR.next()
            return Segment(start, end, Unsorted)
        else:
            # long or isolated short segment: return unchanged
            curr = self.next1
            self.next1 = self.next2
            self.next2 = self.IDR.next()
            return curr

    def finished(self):
        return (self.next1 == None)


# Stage 3: Split long unsorted segments into ones of length in range
# blockMin,...,blockMax (suitable for InsertSort).
# Return a list of all segments.

blockMin = 32
blockMax = 63  # require blockMax >= blockMin*2+1


def segments(L, key=lambda x: x):
    FS = FuseSegments(IncDecRuns(L, key))
    S = []
    curr = FS.next()
    while curr != None:
        if curr.len() == 1 and len(S) >= 1 and not FS.finished():
            # drop this segment, just tag extra element onto previous one
            S[-1].end += 1
        elif curr.tag != Unsorted or curr.len() <= blockMax:
            # keep segment as is
            S.append(curr)
        else:
            # split long unsorted segment into blocks
            start = curr.start
            n = curr.len()
            k = n // blockMin
            divs = [start + (n * i) // k for i in range(k + 1)]
            for i in range(k):
                S.append(Segment(divs[i], divs[i + 1], 0))
        curr = FS.next()
    return S


# TODO: Task 1.
def insertSort(L, start, end, key=lambda x: x):
    for i in range(start, end):
        # use p to record the current element is comparing with other former elements
        p = L[i]
        x = key(L[i])
        j = i - 1
        # if the former element is bigger than the current one by key sorting, put the former one back one place
        while j >= start and key(L[j]) > x:
            L[j + 1] = L[j]
            j = j - 1
        L[j + 1] = p


def reverse(L, start, end):
    end = end - 1  # get the index of last element
    # reverse the list by putting every element one by one
    for i in range((end - start) + 1):
        m = L[start]  # use m to record the first element in the list
        # move all elements before the last put element forward one place
        for j in range((end - start) - i):
            L[start + j] = L[start + j + 1]
        # put the first element in current list one place before the last put element at back
        L[end - i] = m


def processSegments(L, segs, key=lambda x: x):
    for i in range(len(segs)):
        # if the segment is decrease, then reverse it
        if segs[i].tag == -1:
            reverse(L, segs[i].start, segs[i].end)
        # if the segment is unsorted, then use insertSort to let it be sorted
        elif segs[i].tag == 0:
            insertSort(L, segs[i].start, segs[i].end, key)


# TODO: Task 2.
def mergeSegments(L, seg1, seg2, M, start, key=lambda x: x):
    i = seg1.len()  # record the length of segment one
    j = seg2.len()  # record the length of segment two
    # compare the starter of two lists and put the bigger one into M, if neither of them is null.
    while i > 0 and j > 0:
        if key(L[seg1.end - i]) <= key(L[seg2.end - j]):
            M[start + seg1.len() + seg2.len() - i - j] = L[seg1.end - i]
            i = i - 1
        else:
            M[start + seg1.len() + seg2.len() - i - j] = L[seg2.end - j]
            j = j - 1
    # if one of the list is null, the put all elements in other list into M directly
    if i == 0:
        while j > 0:
            M[start + seg1.len() + seg2.len() - i - j] = L[seg2.end - j]
            j = j - 1
    elif j == 0:
        while i > 0:
            M[start + seg1.len() + seg2.len() - i - j] = L[seg1.end - i]
            i = i - 1
    return seg1.len() + seg2.len()  # return the length of the su of two lists


def copySegment(L, seg, M, start):
    lenc = seg.len()  # record the length of elements needed to be put in M
    for i in range(lenc):
        M[start + i] = L[seg.start + i]  # put the elements specified in segment in L into M
    return lenc


# TODO: Task 3.
def mergeRound(L, segs, M, key=lambda x: x):
    even_pairs = len(segs) // 2  # the number of even pairs in list
    current_start = 0  # record the start position of each merge
    segs_M = []  # record the segments in M
    for i in range(even_pairs):
        # merge the i th pair and record the length they used in M
        lens = mergeSegments(L, segs[i * 2], segs[i * 2 + 1], M, current_start, key)
        current_start = current_start + lens  # new start position for next merge
        m = Segment(segs[i * 2].start, segs[i * 2 + 1].end, 1)  # record the new created segment in M
        segs_M.append(m)
    # if the last segment has not pairs, then put it into M directly
    if (len(segs) - even_pairs * 2) != 0:
        copySegment(L, segs[len(segs) - 1], M, current_start)
        m = Segment(segs[len(segs) - 1].start, segs[len(segs) - 1].end, 1)  # record the new created segment in M
        segs_M.append(m)
    return segs_M


def mergeRounds(L, segs, M, key=lambda x: x):
    side = True  # record the direction of merging two lists. If side is true, moving data from L to M and vice versa.
    # merge the list L by another list M for O(lg(n)) times
    while len(segs) > 1:
        if side:
            segs = mergeRound(L, segs, M, key)
            side = False  # change the moving direction for next merge
        else:
            segs = mergeRound(M, segs, L, key)
            side = True  # change the moving direction for next merge
    # if the sorted list is put in M, copy it in L.
    if not side:
        L = M
    return L


# Provided code:

def SimpleTimSort(L, key=lambda x: x):
    if len(L) <= 1:
        return L
    else:
        segs = segments(L,key)
        processSegments(L, segs, key)
        M = [None] * len(L)
        return mergeRounds(L, segs, M, key)

# End of file

