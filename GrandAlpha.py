from math import sqrt,exp
from random import random,choice

from DataStructures import *

class GrandAlpha:
    def __init__(self, facCourseFilename, courseTimesFilename, conflictsFilename):
        # load the information about what courses faculty are teaching
        facCourseFile = open(facCourseFilename, 'r')
        self.allFacCourses = AllFacultyCourses() # this will be the list of faculty schedules
        for line in facCourseFile:
            if len(line.strip()) > 0:
                self.allFacCourses.append(FacultyCourses(line))

        facCourseFile.close()
        
        # TODO: Would be a good idea to check the courses in this to double-check that
        # they are also in the ClassTimes. It is possible that there are extra courses
        # here, and that would cause problems down the road.
        
        # load the information about what possible times each course can be taught at
        courseTimesFile = open(courseTimesFilename, 'r')
        self.allCourseTimes = AllCourseTimes() # this will be the list of faculty schedules
        for line in courseTimesFile:
            if len(line.strip()) > 0:
                self.allCourseTimes.append(CourseTimes(line))

        courseTimesFile.close()
        
        # load the information about the course conflicts that exist that the new
        # schedule must adapt to
        conflictsFile = open(conflictsFilename, 'r')
        self.allConflicts = AllConflicts() # this will be the list of faculty schedules
        for line in conflictsFile:
            if len(line.strip()) > 0:
                els = line.strip().split(',')
                self.allConflicts.append(els[0], els[1], int(els[2]))

        conflictsFile.close()

        # TODO: Would be a good idea to check the courses in this to double-check that
        # they are also in the ClassTimes. It is possible that there are extra courses
        # here, and that could mean course conflicts are not found.

    def CreateRandomScheduleBasic(self):
        return {courseTimes.name: choice(courseTimes.times) for courseTimes in self.allCourseTimes.allCourseTimes}
    
    def CreateRandomScheduleTry(self):
        # TODO: take into account multiple sections of same class
        sch = {}
        for courseTimes in self.allCourseTimes.allCourseTimes:
            otherCoursesToCheck = self.allFacCourses.getFacOtherCoursesByCourse(courseTimes.name)
            otherTimes = []
            for course in otherCoursesToCheck:
                if course in sch:
                    otherTimes.append(sch[course])

            possibletimes = [time for time in courseTimes.times if time not in otherTimes]
            if len(possibletimes) == 0:
                print('Reached an impasse when building initial schedule with trying to schedule courses for ', self.allFacCourses.getFacNameByCourse(courseTimes.name), '. Trying again...', sep = '')
                return {}

            sch[courseTimes.name] = choice(possibletimes)
            
        return sch
    
    def CreateRandomSchedule(self):
        tryCount = 0
        while True:
            tryCount += 1
            if tryCount > 30:
                print('Having trouble creating any schedule based on faculty restrictions given')
                raise Exception
            
            sch = self.CreateRandomScheduleTry()
            if len(sch) != 0:
                return sch
    
    def StepSchedule(self, sch):
        sch = sch.copy()
        
        tryCount = 0
        while True:
            tryCount += 1
            if tryCount > 30:
                print('Having trouble stepping schedule for unknown reason')
                raise Exception
            
            # TODO: take into account multiple sections of same class

            courseToChange = choice(list(sch.keys()))
            courseTimes = self.allCourseTimes.getCourseTimes(courseToChange)
            currentTime = sch[courseToChange]
            
            if len(courseTimes.times) == 1: # If the course only has one time slot available, it cannot be changed
                tryCount -= 1 # don't count this against the total number of trials
                continue

            otherCoursesToCheck = self.allFacCourses.getFacOtherCoursesByCourse(courseToChange)
            otherTimes = []
            for course in otherCoursesToCheck:
                otherTimes.append(sch[course])

            possibletimes = [time for time in courseTimes.times if time not in otherTimes and time != currentTime]
            if len(possibletimes) != 0:
                sch[courseToChange] = choice(possibletimes)
                print(tryCount)
                return sch

    def accumulatePenalties(self, sch):
        # get a dict where the times are the keys and the courses are the values
        inv_sch = {}
        for k, v in sch.items():
            inv_sch.setdefault(v, []).append(k)
        
        totalPenalties = 0
        # TODO: currently assumes that courses must be identical to conflict
        for time, courses in inv_sch.items():
            for i in range(len(courses)):
                for j in range(i + 1, len(courses)):
                    totalPenalties += self.allConflicts.getPenalty(courses[i], courses[j])
        
        return totalPenalties
    
    def anneal(self, sch):
        Tmax = 1000.0
        Tmin = 0.1
        tau = 1e4

        t = 0
        T = Tmax
        penalties = self.accumulatePenalties(sch)
        while T > Tmin:
            
            # show progress
            if t % 100 == 0:
                print('Steps taken:', t)

            # Cooling
            T = Tmax*exp(-t/tau)

            schnew = self.StepSchedule(sch)
            penaltiesnew = self.accumulatePenalties(sch)
            deltaPenalties = penaltiesnew - penalties

            # If the move is rejected, swap them back again
            if random() < exp(-deltaPenalties / T): # accept the new sch according to Boltzmann factor
                sch = schnew
                penalties = penaltiesnew
            
            t += 1
        
        return sch

    def summary(self, sch):
        penalties = self.accumulatePenalties(sch)
        print('The total number of penalties for the schedule is', penalties)
        
        # TODO: need more detail - like where are the penalties coming from?
    
    def exportSch(self, filename, sch):
        outfile = open(filename, 'w')
        for facCourses in self.allFacCourses.allFacCourses:
            for course in facCourses.courses:
                s = facCourses.name + ', ' + course + ', ' + sch[course] + '\n'
                outfile.write(s)
        
        outfile.close()
    
    def importSch(self, filename):
        schFile = open(filename, 'r')
        sch = {}
        for line in schFile:
            if len(line.strip()) > 0:
                linesplit = line.strip().split(',')
                sch[linesplit[1].strip()] = linesplit[2].strip()

        schFile.close()
        return sch
    
    # TODO: What if import contains a faculty conflict?