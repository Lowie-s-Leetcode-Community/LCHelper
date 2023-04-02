import requests
import json

QUERY_DAILY_CHALLENGE = """
query questionOfToday {
    activeDailyCodingChallengeQuestion {
        date
        userStatus
        link
        question {
            acRate
            difficulty
            freqBar
            frontendQuestionId: questionFrontendId
            isFavor
            paidOnly: isPaidOnly
            status
            title
            titleSlug
            hasVideoSolution
            hasSolution
            topicTags {
                name
                id
                slug
            }
        }
    }
}
"""

QUERY_QUESTION_INFO = """
query questionTitle($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        stats
        acRate
        questionId   
        questionFrontendId
        title  
        titleSlug    
        isPaidOnly    
        difficulty   
        likes   
        dislikes
        topicTags {
                name
                id
                slug
            }
        }
    }
"""
QUERY_USER_PROFILE = """
query userPublicProfile($username: String!) {
    matchedUser(username: $username) {
        contestBadge {     
            name      
            expired      
            hoverText      
            icon    
        }    
        username    
        githubUrl    
        twitterUrl    
        linkedinUrl    
        profile {      
            ranking      
            userAvatar      
            realName      
            aboutMe      
            school      
            websites      
            countryName      
            company      
            jobTitle      
            skillTags      
            postViewCount      
            postViewCountDiff      
            reputation    
            reputationDiff      
            solutionCount      
            solutionCountDiff     
            categoryDiscussCount    
            categoryDiscussCountDiff
        }  
    }
}   
"""
QUERY_USER_CALENDAR_INFO = """
query userProfileCalendar($username: String!, $year: Int) {
    matchedUser(username: $username) {
        userCalendar(year: $year) {    
            streak
            totalActiveDays     
        }
    }
}
"""
QUERY_USER_PROBLEM_INFO = """
query userProblemsSolved($username: String!) {
    allQuestionsCount {
        difficulty
        count
    }
    matchedUser(username: $username) {   
        problemsSolvedBeatsStats {      
            difficulty      
            percentage  
        }
        submitStatsGlobal {      
            acSubmissionNum {        
                difficulty        
                count      
            }  
        } 
    }
}

"""
QUERY_USER_CONTEST_INFO = """
query userContestRankingInfo($username: String!) {
    userContestRanking(username: $username) {
        attendedContestsCount    
        rating    
        globalRanking    
        totalParticipants    
        topPercentage    
        badge {      
            name    
        } 
    }
}
"""
QUERY_RECENT_AC = """
query recentAcSubmissions($username: String!, $limit: Int!) {
    recentAcSubmissionList(username: $username, limit: $limit) {
        id  
        title 
        titleSlug    
        timestamp
    }
}
"""

LC_URL = "https://leetcode.com/"
API_URL = "https://leetcode.com/graphql"
LC_LOGO_URL = ""
class LC_utils:
    def get_question_info(title_slug: str):
        payload = {"query": QUERY_QUESTION_INFO, "variables": {"titleSlug": title_slug}}
        response = requests.post(API_URL, json = payload)
        tmp = json.loads(response.content)
        info = tmp['data']['question']

        tmp = json.loads(tmp['data']['question']['stats']) # This is a string for whatever reason
        tag_list = {}
        for i in info['topicTags']:
            tag_list[i['name']] = f"https://leetcode.com/tag/{i['slug']}"

        return {
            'title': info['title'],
            'title_slug': info['titleSlug'],
            'link': LC_URL + 'problems/' + info['titleSlug'],
            'id': info['questionFrontendId'],
            'difficulty': info['difficulty'],
            'ac_rate': info['acRate'],
            'likes': info['likes'],
            'dislikes': info['dislikes'],
            'total_AC': tmp['totalAccepted'],
            'total_submissions': tmp['totalSubmission'],
            'topics': tag_list
        }

    def get_daily_challenge_info():
        payload = {"query": QUERY_DAILY_CHALLENGE}
        response = requests.post(API_URL, json = payload)
        tmp = json.loads(response.content)
        info = tmp['data']['activeDailyCodingChallengeQuestion']
        return {
            'date': info['date'],
            'link': LC_URL[:-1] + info['link'],
            'title': info['question']['title'],
            'title_slug': info['question']['titleSlug']
        }
    
    def get_user_profile(username: str):
        # Public user profile
        payload = {"query": QUERY_USER_PROFILE, "variables": {"username": username}}
        response = requests.post(API_URL, json = payload)
        profile_tmp = json.loads(response.content)
        if not profile_tmp['data']['matchedUser']:
            return None
        profile_info = profile_tmp['data']['matchedUser']['profile']
        profile_json = {
            'name': profile_info['realName'],
            'rank': profile_info['ranking'],
            'avatar': profile_info['userAvatar'],
            'link': LC_URL + username,
            'country': profile_info['countryName'],
            'summary': profile_info['aboutMe']
        }
        
        # Calendar info 
        payload = {"query": QUERY_USER_CALENDAR_INFO, "variables": {"username": username}}
        response = requests.post(API_URL, json = payload)
        calendar_tmp = json.loads(response.content)
        calendar_info = calendar_tmp['data']['matchedUser']['userCalendar']
        calendar_json = {
            'total_active_days': calendar_info['totalActiveDays'],
            'streak': calendar_info['streak']
        }

        # Problem solved info
        payload = {"query": QUERY_USER_PROBLEM_INFO, "variables": {"username": username}}
        response = requests.post(API_URL, json = payload)
        problem_tmp = json.loads(response.content)
        problem_info = problem_tmp['data']
        problem_json = {
            'total_problem':{
                'all': problem_info['allQuestionsCount'][0]['count'],
                'easy': problem_info['allQuestionsCount'][1]['count'],
                'medium': problem_info['allQuestionsCount'][2]['count'],
                'hard': problem_info['allQuestionsCount'][3]['count']
            },
            'solved': {
                'all': problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][0]['count'],
                'easy': problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][1]['count'],
                'medium':problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][2]['count'],
                'hard': problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][3]['count']
            },
            'percentage':{
                'all': round(problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][0]['count']/problem_info['allQuestionsCount'][0]['count']*100, 1),
                'easy': round(problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][1]['count']/problem_info['allQuestionsCount'][1]['count']*100, 1),
                'medium': round(problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][2]['count']/problem_info['allQuestionsCount'][2]['count']*100, 1),
                'hard': round(problem_info['matchedUser']['submitStatsGlobal']['acSubmissionNum'][3]['count']/problem_info['allQuestionsCount'][3]['count']*100, 1),
            }
        }

        # Contest info 
        payload = {"query": QUERY_USER_CONTEST_INFO, "variables": {"username": username}}
        response = requests.post(API_URL, json = payload)
        contest_tmp = json.loads(response.content)
        contest_info = contest_tmp['data']['userContestRanking']
        if contest_info:
            contest_json = {
                'contest_count': contest_info['attendedContestsCount'],
                'rating': int(contest_info['rating']),
                'global_rank': contest_info['globalRanking'],
                'top_percentage': contest_info['topPercentage']
            }
        else: 
            contest_json = {
                'contest_count': None,
                'rating': None,
                'global_rank': None,
                'top_percentage': None
            }
        
        return {
            'profile': profile_json,
            'calendar': calendar_json,
            'problem': problem_json,
            'contest': contest_json
        }
    
    def get_recent_ac(username: str):
        payload = {"query": QUERY_RECENT_AC, "variables": {"username": username, "limit": 5}}
        response = requests.post(API_URL, json = payload)
        recent_tmp = json.loads(response.content)
        recent_list = recent_tmp['data']['recentAcSubmissionList']
        
        return recent_list
