import json
from datetime import datetime

import requests

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
    userContestRankingHistory(username: $username) {
        attended
        rating
        ranking
        trendDirection
        problemsSolved
        totalProblems
        finishTimeInSeconds
        contest {
            title
            startTime
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
        langName
        runtime
        memory
    }
}
"""

QUERY_QUESTION_LIST = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
    problemsetQuestionList: questionList(    
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip    
        filters: $filters
    ) 
    {
        total: totalNum
        questions: data {
            acRate      
            difficulty      
            freqBar     
            frontendQuestionId: questionFrontendId
            isFavor      
            paidOnly: isPaidOnly
            status
            title      
            titleSlug      
            topicTags {        
                name        
                id        
                slug      
            }
            hasSolution
            hasVideoSolution
        }
    }
}
"""

LC_URL = "https://leetcode.com/"
API_URL = "https://leetcode.com/graphql"
LC_LOGO_URL = ""


class LC_utils:
    def get_problem_info(title_slug: str):
        payload = {"query": QUERY_QUESTION_INFO, "variables": {"titleSlug": title_slug}}
        response = requests.post(API_URL, json=payload)
        tmp = json.loads(response.content)
        info = tmp["data"]["question"]

        tmp = json.loads(
            tmp["data"]["question"]["stats"]
        )  # This is a string for whatever reason
        tag_list = {}
        for i in info["topicTags"]:
            tag_list[i["name"]] = f"https://leetcode.com/tag/{i['slug']}"

        return {
            "title": info["title"],
            "title_slug": info["titleSlug"],
            "link": LC_URL + "problems/" + info["titleSlug"],
            "id": info["questionFrontendId"],
            "difficulty": info["difficulty"],
            "ac_rate": info["acRate"],
            "likes": info["likes"],
            "dislikes": info["dislikes"],
            "total_AC": tmp["totalAccepted"],
            "total_submissions": tmp["totalSubmission"],
            "topics": tag_list,
        }

    def crawl_problem_list():
        payload = {
            "query": QUERY_QUESTION_LIST,
            "variables": {"categorySlug": "", "skip": 0, "limit": 3600, "filters": {}},
        }
        response = requests.post(API_URL, json=payload)

        if not response.ok or not response.content:
            return []

        tmp = json.loads(response.content)
        return tmp["data"]["problemsetQuestionList"]["questions"]

    def get_daily_challenge_info():
        payload = {"query": QUERY_DAILY_CHALLENGE}
        response = requests.post(API_URL, json=payload)
        tmp = json.loads(response.content)
        info = tmp["data"]["activeDailyCodingChallengeQuestion"]
        return {
            "date": info["date"],
            "link": LC_URL[:-1] + info["link"],
            "title": info["question"]["title"],
            "title_slug": info["question"]["titleSlug"],
            "id": info["question"]["frontendQuestionId"],
        }

    def get_user_profile(username: str):
        # Public user profile
        payload = {"query": QUERY_USER_PROFILE, "variables": {"username": username}}
        response = requests.post(API_URL, json=payload)
        profile_tmp = json.loads(response.content)
        if not profile_tmp["data"]["matchedUser"]:
            return None
        profile_info = profile_tmp["data"]["matchedUser"]["profile"]
        profile_json = {
            "name": profile_info["realName"],
            "rank": profile_info["ranking"],
            "avatar": profile_info["userAvatar"],
            "link": LC_URL + username,
            "country": profile_info["countryName"],
            "summary": profile_info["aboutMe"],
        }

        # Calendar info
        payload = {
            "query": QUERY_USER_CALENDAR_INFO,
            "variables": {"username": username},
        }
        response = requests.post(API_URL, json=payload)
        calendar_tmp = json.loads(response.content)
        calendar_info = calendar_tmp["data"]["matchedUser"]["userCalendar"]
        calendar_json = {
            "total_active_days": calendar_info["totalActiveDays"],
            "streak": calendar_info["streak"],
        }

        # Problem solved info
        payload = {
            "query": QUERY_USER_PROBLEM_INFO,
            "variables": {"username": username},
        }
        response = requests.post(API_URL, json=payload)
        problem_tmp = json.loads(response.content)
        problem_info = problem_tmp["data"]
        problem_json = {"total_problem": {}, "solved": {}, "percentage": {}}
        diffs = ["all", "easy", "medium", "hard"]
        for i in range(4):
            problem_json["total_problem"][diffs[i]] = problem_info["allQuestionsCount"][
                i
            ]["count"]
            problem_json["solved"][diffs[i]] = problem_info["matchedUser"][
                "submitStatsGlobal"
            ]["acSubmissionNum"][i]["count"]
            problem_json["percentage"][diffs[i]] = (
                round(
                    problem_json["solved"][diffs[i]]
                    / problem_json["total_problem"][diffs[i]]
                    * 100,
                    1,
                ),
            )

        # Contest info
        payload = {
            "query": QUERY_USER_CONTEST_INFO,
            "variables": {"username": username},
        }
        response = requests.post(API_URL, json=payload)
        contest_tmp = json.loads(response.content)
        contest_info = contest_tmp["data"]["userContestRanking"]
        if contest_info:
            contest_json = {
                "contest_count": contest_info["attendedContestsCount"],
                "rating": int(contest_info["rating"]),
                "global_rank": contest_info["globalRanking"],
                "top_percentage": contest_info["topPercentage"],
            }
        else:
            contest_json = {
                "contest_count": None,
                "rating": None,
                "global_rank": None,
                "top_percentage": None,
            }

        return {
            "profile": profile_json,
            "calendar": calendar_json,
            "problem": problem_json,
            "contest": contest_json,
        }

    def get_recent_ac(username: str, limit: int):
        payload = {
            "query": QUERY_RECENT_AC,
            "variables": {"username": username, "limit": limit},
        }
        try:
            response = requests.post(API_URL, json=payload)
            recent_tmp = json.loads(response.content)
            recent_list = recent_tmp["data"]["recentAcSubmissionList"]
        except Exception:
            print(f"Warning, crawl failed for user {username}. Please try again!")
            return []
        return recent_list

    def get_contest_list():
        community_account = "lwleetcodeclass"
        payload = {
            "query": QUERY_USER_CONTEST_INFO,
            "variables": {"username": community_account},
        }
        try:
            response = requests.get(API_URL, json=payload)
            resp_content = json.loads(response.content)
            ranking_history = resp_content["data"]["userContestRankingHistory"]
            contest_history = list(map(lambda x: x["contest"], ranking_history))
        except Exception as exc:
            print(f"Retrieve contest list unsuccessfully. {exc}")
            return []
        return contest_history

    def get_next_contests_info():
        def extract_contests_id(contest_name: str) -> int:
            str = contest_name.split()[2]
            digits = "".join(c for c in str if c.isdigit())

            return int(digits) if digits else 0

        def generate_next_contests(last: dict, type: str) -> list:
            week = 60 * 60 * 24 * 7
            ts = last["timestamp"]
            delta = 2 if type == "biweekly" else 1
            res = []
            cid = last["contestId"]
            while ts - week * delta < datetime.now().timestamp():
                res.append({"type": type, "timestamp": ts, "contestId": cid})
                ts += week * delta
                cid += 1
            return res

        contest_list = LC_utils.get_contest_list()
        latests = {
            "weekly": {"timestamp": 0, "contestId": 0},
            "biweekly": {"timestamp": 0, "contestId": 0},
        }
        for c in contest_list:
            c_name = str(c["title"])
            c_type = c_name.split()[0]
            c_stamp = c["startTime"]
            if c_type == "Biweekly":
                if c_stamp < latests["biweekly"]["timestamp"]:
                    continue
                latests["biweekly"] = {
                    "timestamp": c_stamp,
                    "contestId": int(extract_contests_id(c_name)),
                }
                continue
            if c_type == "Weekly":
                if c_stamp < latests["weekly"]["timestamp"]:
                    continue
                latests["weekly"] = {
                    "timestamp": c_stamp,
                    "contestId": int(extract_contests_id(c_name)),
                }

        res = []
        for type, last in latests.items():
            res += generate_next_contests(last, type)
        res.sort(key=lambda x: -x["timestamp"])
        return res
