class FacultyCourses:
    def __init__(self, line):
        line = line.strip()
        elements = line.split(',')
        self.name = elements.pop(0)
        self.courses = elements.copy()
        self.dept = CourseTimes.getCourseDept(self.courses[0])
        
    def contains(self, course):
        return course in self.courses
    
    def print(self):
        print(self.name, 'in', self.dept, 'has courses ', end = '')
        for course in self.courses:
            print(course, ' ', end = '', sep = '')


class AllFacultyCourses:
    def __init__(self):
        self.allFacCourses = []
    
    def append(self, facCourses):
        self.allFacCourses.append(facCourses)
    
    def getFacCourses(self, name):
        if type(name) == int:
            return self.allFacCourses[name]
        elif type(name) == str:
            for facCourses in self.allFacCourses:
                if facCourses.name == name:
                    return facCourses
            return None
        return None
    
    def getFacByCourse(self, course):
        for facCourses in self.allFacCourses:
            if facCourses.contains(course):
                return facCourses
        print('There are no faculty assigned to teach ', course, '!')
        return None
    
    def getFacNameByCourse(self, course):
        facCourses = self.getFacByCourse(course)
        return facCourses.name
    
    def getFacOtherCoursesByCourse(self, course):
        facCourses = self.getFacByCourse(course)
        courses = []
        for el in facCourses.courses:
            if el != course:
                courses.append(el)
        return courses
    
    def print(self):
        for facCourses in self.allFacCourses:
            facCourses.print()
            print()


class CourseTimes:
    def __init__(self, line):
        line = line.strip()
        elements = line.split(',')
        self.name = elements.pop(0)
        #self.maxsize = elements.pop(0)
        self.times = elements.copy()
    
    def contains(self, time):
        return time in self.times
    
    def isCourseNameMultiSection(name):
        return '-' in name
    
    def isCourseMultiSection(self):
        return CourseTimes.isCourseNameMultiSection(self.name)
    
    def getCourseNum(name):
        numstart = 4
        hyphenpos = name.find('-')
        if hyphenpos > 0:
            return name[numstart:hyphenpos]
        else:
            return name[numstart:]
    
    def getCourseSectionNum(name):
        hyphenpos = name.find('-')
        if hyphenpos > 0:
            return '0' + name[hyphenpos + 1]
        else:
            return '01'
    
    def getCourseDept(name):
        code = CourseTimes.getCourseDeptCode(name)
        if code == 'CSCI' or code == 'ISYS':
            dept = 'Computer Science'
        elif code == 'CHEM' or code == 'NSCI':
            dept = 'Chemistry'
        elif code == 'PHYS':
            dept = 'Physics'
        elif code == 'MATH' or code == 'STAT' or code == 'DAST' or code == 'DAIC':
            dept = 'Math'
        elif code == 'BIOL' or code == 'ENVS':
            dept = 'Biology'
        elif code == 'FREX' or code == 'PHIL':
            dept = 'Biology'
        else:
            dept = 'Unknown'
            print('Unknown department with code', code)
        
        return dept
    
    def getCourseDeptCode(name):
        code = name[0:4]
        
        return code
    
    def getDayTime(time):
        # TODO: math has some 4 hour courses that I need to adjust the time for (see Reza email 2/20/2019)
        if time == 'MWF8':
            day = 'MWF'; start = '8:00AM'; end = '8:50AM'
        elif time == 'MWF9':
            day = 'MWF'; start = '9:00AM'; end = '9:50AM'
        elif time == 'MWF10:30':
            day = 'MWF'; start = '10:30AM'; end = '11:20AM'
        elif time == 'MWF11:30':
            day = 'MWF'; start = '11:30AM'; end = '12:20PM'
        elif time == 'MW8':
            day = 'MW'; start = '8:00AM'; end = '8:50AM'
        elif time == 'MW9':
            day = 'MW'; start = '9:00AM'; end = '9:50AM'
        elif time == 'MW10:30':
            day = 'MW'; start = '10:30AM'; end = '11:20AM'
        elif time == 'MW11:30':
            day = 'MW'; start = '11:30AM'; end = '12:20PM'
        elif time == 'MWF1':
            day = 'MWF'; start = '1:00PM'; end = '1:50PM'
        elif time == 'MWF2:30':
            day = 'MWF'; start = '2:30PM'; end = '3:20PM'
        elif time == 'MW1':
            day = 'MW'; start = '1:00PM'; end = '2:15PM'
        elif time == 'MW2:30':
            day = 'MW'; start = '2:30PM'; end = '3:45PM'
        elif time == 'M1-4':
            day = 'M'; start = '1:00PM'; end = '4:00PM'
        elif time == 'M1-5':
            day = 'M'; start = '1:00PM'; end = '5:00PM'
        elif time == 'W1-4':
            day = 'W'; start = '1:00PM'; end = '4:00PM'
        elif time == 'W1-5':
            day = 'W'; start = '1:00PM'; end = '5:00PM'
        elif time == 'TR8':
            day = 'TR'; start = '8:00AM'; end = '9:15AM'
        elif time == 'TR10:30':
            day = 'TR'; start = '10:30AM'; end = '11:45AM'
        elif time == 'TR1':
            day = 'TR'; start = '1:00PM'; end = '2:15PM'
        elif time == 'TR2:30':
            day = 'TR'; start = '2:30PM'; end = '3:45PM'
        elif time == 'T1-4':
            day = 'T'; start = '1:00PM'; end = '4:00PM'
        elif time == 'T1-5':
            day = 'T'; start = '1:00PM'; end = '5:00PM'
        elif time == 'R1-4':
            day = 'R'; start = '1:00PM'; end = '4:00PM'
        elif time == 'R1-5':
            day = 'R'; start = '1:00PM'; end = '5:00PM'
        elif time == 'MW4':
            day = 'MW'; start = '4:00PM'; end = '5:15PM'
        elif time == 'MWF10:30-12:20':
            day = 'MWF'; start = '10:30AM'; end = '12:20PM'
        elif time == 'F1':
            day = 'F'; start = '1:00PM'; end = '1:50PM'
        elif time == 'F1:30':
            day = 'F'; start = '1:30PM'; end = '3:30PM'
        elif time == 'F2':
            day = 'F'; start = '2:00PM'; end = '2:50PM'
        elif time == 'F2:30':
            day = 'F'; start = '2:30PM'; end = '4:00PM'
        elif time == 'M6':
            day = 'M'; start = '6:00PM'; end = '?'
        elif time == 'T6':
            day = 'T'; start = '6:00PM'; end = '?'
        elif time == 'T6-9':
            day = 'T'; start = '6:00PM'; end = '9:00PM'
        elif time == 'W6':
            day = 'W'; start = '6:00PM'; end = '?'
        elif time == 'M8':
            day = 'M'; start = '8:00AM'; end = '8:50AM'
        elif time == 'T8':
            day = 'T'; start = '8:00AM'; end = '8:50AM'
        elif time == 'W8':
            day = 'W'; start = '8:00AM'; end = '8:50AM'
        elif time == 'M2:30':
            day = 'M'; start = '2:30PM'; end = '4:30PM'
        elif time == 'T9:30-12:30':
            day = 'T'; start = '9:30AM'; end = '12:30PM'
        elif time == 'T6-8:20':
            day = 'T'; start = '6:00PM'; end = '8:20PM'
        else:
            print('not able to identify time label', time)
            return time, time, time
        
        return day, start, end
    
    def print(self):
        print(self.name, 'has available times ', end = '')
        for time in self.times:
            print(time, ' ', end = '', sep = '')


class AllCourseTimes:
    def __init__(self):
        self.allCourseTimes = []
    
    def append(self, courseTimes):
        self.allCourseTimes.append(courseTimes)
    
    def getAllCourses(self):
        return [courseTimes.name for courseTimes in self.allCourseTimes]
    
    def getCourseTimes(self, name):
        if type(name) == int:
            return self.allCourseTimes[name]
        elif type(name) == str:
            for courseTimes in self.allCourseTimes:
                if courseTimes.name == name:
                    return courseTimes
            return None
        return None
    
    def print(self):
        for courseTimes in self.allCourseTimes:
            courseTimes.print()
            print()


class Conflict:
    def __init__(self, course1, course2, priority):
        if course1 > course2:
            course1, course2 = course2, course1
        self.course1 = course1
        self.course2 = course2
        self.priority = int(priority)
    
    def print(self):
        print(self.course1, 'and', self.course2, 'conflict with priority', self.priority)


class AllConflicts:
    def __init__(self):
        self.allConflicts = []
    
    def add(self, course1, course2, priority = 5):
        conflict = self.getConflict(course1, course2)
        if conflict == None:
            self.allConflicts.append(Conflict(course1, course2, priority))
        else:
            conflict.priority += int(priority)

    def getConflict(self, course1, course2):
        if course1 > course2:
            course1, course2 = course2, course1
        for conflict in self.allConflicts:
            if conflict.course1 == course1 and conflict.course2 == course2:
                return conflict
        return None
    
    def getPenalty(self, course1, course2):
        # for tests that involve courses that have more than one section, assume no conflicts
        if CourseTimes.isCourseNameMultiSection(course1) or CourseTimes.isCourseNameMultiSection(course2):
            return 0
        
        if course1 > course2:
            course1, course2 = course2, course1
        for conflict in self.allConflicts:
            if course1 == conflict.course1 and course2 == conflict.course2:
                return conflict.priority
        return 0
    
    def print(self):
        for conflict in self.allConflicts:
            conflict.print()

            
class TimeConflict:
    def __init__(self, time1, time2):
        if time1 > time2:
            time1, time2 = time2, time1
        self.time1 = time1
        self.time2 = time2
    
    def print(self):
        print(self.time1, 'and', self.time2, 'conflict')


class StudentCourses:
    def __init__(self, line):
        line = line.strip()
        elements = line.split(',')
        self.name = elements.pop(0)
        self.priority = int(elements.pop(0))
        self.courses = elements.copy()
    
    def print(self):
        print(self.name, 'with priority', self.priority, 'has courses ', end = '')
        for course in self.courses:
            print(course, ' ', end = '', sep = '')
        print()
