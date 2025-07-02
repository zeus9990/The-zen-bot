import motor.motor_asyncio
import config
from datetime import datetime, timezone
import random

# data_set = {
#     "userid": 727792852859059,
#     "username": "zeus",
#     "shards": 980,
#     "role_shards": 1000,
#     "roles": {"472874782773587": {"reward":2000, "claimed": True},
#               "148723488487475": {"reward":500, "claimed": False}},
#     "wallet": "none",
#     "quiz_data": {"played": False, "total_quizzes": 0, "last_points": 0, "last_quiz": "28-06-2025"},
#     "checkin_data": {"checked_in": False, "total_checkins": 0, "last_checkin_points": 0, "last_checkin": "28-06-2025"},
#     "played_quizzes": []
# }

# quiz_data = {
#     "question": "what's the color of the sky?",
#     "options": {"A": "Red", "B": "Blue", "C": "Green", "D": "Yellow"},
#     "correct": "Blue"
# }

database = motor.motor_asyncio.AsyncIOMotorClient(config.DB_URL)
zenrock = database["Zenrock"]
userdata = zenrock["userdata"]
quizzes = zenrock["quiz_que"]
date = zenrock["date"]

# Get date
async def get_date(set_date = None):
    if not set_date:
        data = await date.find_one({})
        return data['date']
    else:
        await date.update_one({}, {"$set": {"date": set_date}})
# Get rank
async def get_rank(userid: int) -> dict:
    user_doc = await userdata.find_one({"userid": userid})
    if not user_doc:
        return {
            "success": False,
            "message": f"Sorry <@{userid}> you're not registered yet. Please do a check in to get started."
        }

    user_points = user_doc.get("shards", 0) + user_doc.get("role_shards", 0)

    higher_count = await userdata.count_documents({
        "$expr": {"$gt": [{"$add": ["$shards", "$role_shards"]}, user_points]}
    })

    return {
        "success": True,
        "message": {"username": user_doc['username'], "shards": user_points, "rank": higher_count + 1} 
    }

## Get Leaderboard and rank
async def get_leaderboard(userid: int = None) -> str:
    pipeline_top_10 = [
        {
            "$project": {
                "userid": 1,
                "username": 1,
                "points": {"$add": ["$shards", "$role_shards"]}
            }
        },
        {"$sort": {"points": -1}},
        {"$limit": 10}
    ]
    top_users = await userdata.aggregate(pipeline_top_10).to_list(length=10)

    result_lines = []
    for i, user in enumerate(top_users, start=1):
        result_lines.append(f"> • **{str(i).zfill(2)}. {user['username']} - `{user['points']}` Shards**")

    if userid:
        user_doc = await userdata.find_one({"userid": userid})
        if user_doc:
            user_points = user_doc.get("shards", 0) + user_doc.get("role_shards", 0)
            higher_count = await userdata.count_documents({
                "$expr": {"$gt": [{"$add": ["$shards", "$role_shards"]}, user_points]}
            })
            rank = higher_count + 1
            result_lines.append(f"\n• **Your Rank: {str(rank).zfill(2)}. {user_doc['username']} - `{user_points}` Shards.**")
        else:
            result_lines.append("\n• `You are not registered yet, Check in to get registered.`")

    return "\n".join(result_lines)

## Add Shards
async def add_shards(userid: int, shards: int) -> dict:
    updated = await userdata.update_one({'userid': userid}, {'$inc': {'shards': shards}})
    if updated.matched_count == 0:
        return {"success": False, "message": "User not found!"}
    return {"success": True, "message": f"{shards} shards added to <@{userid}>!"}

## Remove Shards
async def remove_shards(userid: int, shards: int) -> dict:
    updated = await userdata.update_one({'userid': userid}, {'$inc': {'shards': -shards}})
    if updated.matched_count == 0:
        return {"success": False, "message": "User not found!"}
    return {"success": True, "message": f"{shards} shards removed from <@{userid}>!."}

## User info
async def get_user(userid: int) -> dict:
    user_details = await userdata.find_one({'userid': userid})
    if user_details:
        return {"success": True, "message": user_details}
    else:
        return {"success": False, "message": "User not Found."}

# Daily Check in
async def daily_checkin(userid: int, username: str) -> dict:
    today_str = datetime.now(timezone.utc).date().isoformat()
    user = await userdata.find_one({"userid": userid})
    earned = random.randint(2, 6)

    if user:
        last_checkin = user.get("checkin_data", {}).get("last_checkin", "")
        if last_checkin == today_str:
            return {"success": False, "message": f"Hey <@{userid}> you've already checked in today."}

        await userdata.update_one({
            "userid": userid
            },
            {
                "$inc": {
                    "shards": earned,
                    "checkin_data.total_checkins": 1
                },
                "$set": {
                    "checkin_data.checked_in": True,
                    "checkin_data.last_checkin_points": earned,
                    "checkin_data.last_checkin": today_str
                }
            }
        )
    else:
        await userdata.insert_one(
            {
                "userid": userid,
                "username": username,
                "shards": earned,
                "role_shards": 0,
                "roles": {},
                "wallet": None,
                "quiz_data": {"played": False, "total_quizzes": 0, "last_points": 0, "last_quiz": ""},
                "checkin_data": {"checked_in": True, "total_checkins": 1, "last_checkin_points": earned, "last_checkin": today_str},
                "played_quizzes": []
            }
        )
    return {"success": True, "message": f"Congratulations <@{userid}> check-in successfull! You received {earned} shards."}

# Daily Quiz
async def get_daily_quiz(user_id: int) -> dict:
    user = await get_user(userid=user_id)
    if not user['success']:
        return {"success": False, "message": f"Hey <@{user_id}> you're not registered, do a daily check-in to register with the system."}

    quiz_data = user['message']["quiz_data"]
    played_quizzes = user['message']["played_quizzes"]
    
    # Check if already played today
    today_str = datetime.now(timezone.utc).date().isoformat()
    if quiz_data.get("played") and quiz_data.get("last_quiz") == today_str:
        return {"success": False, "message": f"Hey <@{user_id}> love your energy but you have already played the quiz today."}

    # Find a random unseen quiz
    pipeline = [
        {"$match": {"_id": {"$nin": played_quizzes}}},
        {"$sample": {"size": 1}}
    ]
    unseen_quiz = await quizzes.aggregate(pipeline).to_list(length=1)
    if unseen_quiz:
        quiz = unseen_quiz[0]
        return {"success": True, "message": quiz}
    else:
        return {"success": False, "message": f"Hey <@{user_id}> seems like you've finished all the available quizzes."}
    

# Submit Quiz Answer
async def submit_answer(user_id: int, quiz_id: str, selected_answer: str) -> dict:
    quiz = await quizzes.find_one({"_id": quiz_id})

    correct = quiz["correct"].strip().lower() == selected_answer.strip().lower()
    today_str = datetime.now(timezone.utc).date().isoformat()
    if correct:
        points_awarded = random.randint(10, 30)

        update = {
            "$inc": {
                "quiz_data.total_quizzes": 1,
                "shards": points_awarded
            },
            "$set": {
                "quiz_data.last_points": points_awarded
            },
            "$set": {
                "quiz_data.played": True,
                "quiz_data.last_quiz": today_str
            },
            "$push": {
                "played_quizzes": quiz_id
            }
        }

        await userdata.update_one({"userid": user_id}, update)
        return {"success": True, "message": f"Congratulations you won {points_awarded} Shards!"}
    else:
        update = {
            "$inc": {
                "quiz_data.total_quizzes": 1,
                "shards": 0
            },
            "$set": {
                "quiz_data.last_points": 0
            },
            "$set": {
                "quiz_data.played": True,
                "quiz_data.last_quiz": today_str
            },
            "$push": {
                "played_quizzes": quiz_id
            }
        }
        await userdata.update_one({"userid": user_id}, update)
        return {"success": False, "message": f"Oops <@{user_id}>! Your answer was incorrect. Better luck next time!"}

# Add/Remove Roles
async def add_remove_role(user_id: int, role_id: str, reward: int, remove: bool) -> None:
    if not remove:
        user = await userdata.find_one({"userid": user_id})
        if user:
            roles = user.get("roles", {})
            if role_id not in roles:
                await userdata.update_one(
                    {"userid": user_id},
                    {"$set": {f"roles.{role_id}": {"reward": reward, "claimed": False}}}
                )
        return {"success": True, "message": f"Added role: {role_id} to User: {user_id}"}
    else:
        user = await userdata.find_one({"userid": user_id})
        roles = user.get("roles", {})
        if role_id in roles:
            is_claimed = roles[role_id]['claimed']
            updates = {
                "$unset": {f"roles.{role_id}": ""}
            }
            if is_claimed:
                updates["$inc"] = {"role_shards": -reward}

            await userdata.update_one({"userid": user_id}, updates)
        return {"success": True, "message": f"Removed role: {role_id} to From: {user_id}"}

# Claim Role Shards
async def claim_role_reward(user_id: int, role_id: str) -> dict:
    user = await userdata.find_one({"userid": user_id})
    if not user:
        return {"success": False, "message": f"Hey <@{user_id}> you're not registered, do a daily check-in to register with the system."}

    roles = user.get("roles", {})
    role = roles.get(role_id)

    # Check if the role and reward exist
    if not role:
        return {"success": False, "message": f"Hey <@{user_id}> this role isn't currently assigned to your profile or may not have updated yet. Please try again in a few moments."}
    if role.get("claimed"):
        return {"success": False, "message": f"Oops <@{user_id}> looks like the reward for this <@&{role_id}> role is already claimed."}

    reward_amount = role["reward"]

    # Update user's role_shards and mark role as claimed
    await userdata.update_one(
        {"userid": user_id},
        {
            "$inc": {"role_shards": reward_amount},
            "$set": {f"roles.{role_id}.claimed": True}
        }
    )
    return {"success": True, "message": f"Congratulations <@{user_id}> you've successfully claimed {reward_amount} Shards for <@&{role_id}> role."}

async def reset_daily_flags() -> dict:
    await userdata.update_many(
        {},
        {
            "$set": {
                "quiz_data.played": False,
                "checkin_data.checked_in": False
            }
        }
    )
    return {"success": True, "message": "Daily flags reset completed."}