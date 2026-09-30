"""Flask web application for managing blog posts with full CRUD functionality."""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

# (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"  # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'  # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_direction = request.args.get("direction")
    sort_by = request.args.get("sort")
    posts_list = POSTS
    if sort_direction not in ["asc", "desc", None]:
        return jsonify(
            {"error": "Invalid sort direction. Must be 'asc' or 'desc'"}), 400
    if sort_by not in ["title", "content", None]:
        return jsonify(
            {"error": "Invalid sort by. Must be 'title' or 'content'"}), 400

    if (sort_by is None) != (sort_direction is None):
        return jsonify(
            {"error": "Both 'sort' and 'direction' must be provided together."}), 400

    if sort_by and sort_direction:
        is_reverse = sort_direction == "desc"
        posts_list = sorted(
            posts_list,
            key=lambda x: x[sort_by].lower(),
            reverse=is_reverse)

    return jsonify(posts_list)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    required_fields = ["title", "content"]
    missing = [field for field in required_fields if not data.get(field)]

    if missing:
        return (
            jsonify({"message": f"missing required data: {', '.join(missing)}"}),
            400,
        )

    new_id = max((post["id"] for post in POSTS), default=0) + 1
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]}
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id: int):
    global POSTS
    original_length = len(POSTS)
    POSTS = [post for post in POSTS if post["id"] != id]
    if original_length == len(POSTS):
        return jsonify({"message": f"Post with id  {id} does not exist."}), 404
    return jsonify(
        {"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id: int):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    title = data.get("title")
    content = data.get("content")

    if title is None and content is None:
        return jsonify(
            {"message": "At least title or content must be provided"}), 400

    post = next((p for p in POSTS if p["id"] == id), None)
    if post is None:
        return jsonify({"message": f"Post with id {id} does not exist."}), 404
    if title is not None:
        post["title"] = title
    if content is not None:
        post["content"] = content
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get("title", "").strip().lower()
    content_query = request.args.get("content", "").strip().lower()
    if not title_query and not content_query:
        return jsonify([]), 200

    results = [
        post for post in POSTS
        if (title_query and title_query in post["title"].lower())
        or (content_query and content_query in post["content"].lower())
    ]

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
