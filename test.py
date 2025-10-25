import os

def create_file(file_path):
    """Tạo file rỗng nếu chưa tồn tại."""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass
        print(f"Created file: {file_path}")
    else:
        print(f"File already exists: {file_path}")

def create_directory(dir_path):
    """Tạo thư mục nếu chưa tồn tại."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

def generate_project_structure():
    """Tạo cấu trúc thư mục và file cho dự án TTNM-Game."""
    base_path = os.path.join("TTNM-Game", "be")
    create_directory(base_path)

    # controllers/
    controllers_path = os.path.join(base_path, "controllers")
    create_directory(controllers_path)
    controller_files = [
        "games_controller.py",
        "analytics_controller.py",
        "sessions_controller.py",
        "users_controller.py"
    ]
    for file in controller_files:
        create_file(os.path.join(controllers_path, file))

    # models/
    models_path = os.path.join(base_path, "models")
    create_directory(models_path)
    
    # models/games/
    models_games_path = os.path.join(models_path, "games")
    create_directory(models_games_path)
    models_games_files = ["game.py", "emotion.py", "face_component.py"]
    for file in models_games_files:
        create_file(os.path.join(models_games_path, file))
    
    # models/analytics/
    models_analytics_path = os.path.join(models_path, "analytics")
    create_directory(models_analytics_path)
    models_analytics_files = ["child_progress.py", "report.py"]
    for file in models_analytics_files:
        create_file(os.path.join(models_analytics_path, file))
    
    # models/sessions/
    models_sessions_path = os.path.join(models_path, "sessions")
    create_directory(models_sessions_path)
    models_sessions_files = ["game_content.py", "game_data.py", "session.py"]
    for file in models_sessions_files:
        create_file(os.path.join(models_sessions_path, file))
    
    # models/users/
    models_users_path = os.path.join(models_path, "users")
    create_directory(models_users_path)
    models_users_files = ["user.py", "child.py", "admin.py"]
    for file in models_users_files:
        create_file(os.path.join(models_users_path, file))

    # domain/
    domain_path = os.path.join(base_path, "domain")
    create_directory(domain_path)
    
    # domain/games/
    domain_games_path = os.path.join(domain_path, "games")
    create_directory(domain_games_path)
    create_file(os.path.join(domain_games_path, "game.py"))
    
    # domain/games/game_components/
    game_components_path = os.path.join(domain_games_path, "game_components")
    create_directory(game_components_path)
    game_components_files = [
        "recognition_component.py",
        "expression_component.py",
        "face_builder_component.py",
        "who_is_who_component.py",
        "situation_emotion_component.py"
    ]
    for file in game_components_files:
        create_file(os.path.join(game_components_path, file))
    
    # domain/analytics/
    domain_analytics_path = os.path.join(domain_path, "analytics")
    create_directory(domain_analytics_path)
    domain_analytics_files = ["child_progress.py", "report.py"]
    for file in domain_analytics_files:
        create_file(os.path.join(domain_analytics_path, file))
    
    # domain/sessions/
    domain_sessions_path = os.path.join(domain_path, "sessions")
    create_directory(domain_sessions_path)
    domain_sessions_files = ["game_content.py", "game_data.py", "session.py"]
    for file in domain_sessions_files:
        create_file(os.path.join(domain_sessions_path, file))
    
    # domain/users/
    domain_users_path = os.path.join(domain_path, "users")
    create_directory(domain_users_path)
    domain_users_files = ["user.py", "child.py", "admin.py"]
    for file in domain_users_files:
        create_file(os.path.join(domain_users_path, file))
    
    # domain/events/
    domain_events_path = os.path.join(domain_path, "events")
    create_directory(domain_events_path)
    domain_events_files = [
        "game_completed.py",
        "emotion_recognized.py",
        "emotion_missed.py",
        "progress_updated.py",
        "session_started.py"
    ]
    for file in domain_events_files:
        create_file(os.path.join(domain_events_path, file))

    # repository/
    repository_path = os.path.join(base_path, "repository")
    create_directory(repository_path)
    repository_files = [
        "base_repo.py",
        "games_repo.py",
        "analytics_repo.py",
        "sessions_repo.py",
        "users_repo.py"
    ]
    for file in repository_files:
        create_file(os.path.join(repository_path, file))

    # mapper/
    mapper_path = os.path.join(base_path, "mapper")
    create_directory(mapper_path)
    mapper_files = [
        "games_mapper.py",
        "analytics_mapper.py",
        "sessions_mapper.py",
        "users_mapper.py"
    ]
    for file in mapper_files:
        create_file(os.path.join(mapper_path, file))

    # schemas/
    schemas_path = os.path.join(base_path, "schemas")
    create_directory(schemas_path)
    
    # schemas/games/
    schemas_games_path = os.path.join(schemas_path, "games")
    create_directory(schemas_games_path)
    schemas_games_files = [
        "game_request.py",
        "game_response.py",
        "emotion_response.py",
        "face_component_response.py"
    ]
    for file in schemas_games_files:
        create_file(os.path.join(schemas_games_path, file))
    
    # schemas/analytics/
    schemas_analytics_path = os.path.join(schemas_path, "analytics")
    create_directory(schemas_analytics_path)
    schemas_analytics_files = ["progress_request.py", "report_response.py"]
    for file in schemas_analytics_files:
        create_file(os.path.join(schemas_analytics_path, file))
    
    # schemas/sessions/
    schemas_sessions_path = os.path.join(schemas_path, "sessions")
    create_directory(schemas_sessions_path)
    schemas_sessions_files = ["session_request.py", "session_response.py"]
    for file in schemas_sessions_files:
        create_file(os.path.join(schemas_sessions_path, file))
    
    # schemas/users/
    schemas_users_path = os.path.join(schemas_path, "users")
    create_directory(schemas_users_path)
    schemas_users_files = ["user_request.py", "user_response.py"]
    for file in schemas_users_files:
        create_file(os.path.join(schemas_users_path, file))
    
    # schemas/cv/
    schemas_cv_path = os.path.join(schemas_path, "cv")
    create_directory(schemas_cv_path)
    schemas_cv_files = ["cv_request.py", "cv_response.py"]
    for file in schemas_cv_files:
        create_file(os.path.join(schemas_cv_path, file))

    # services/
    services_path = os.path.join(base_path, "services")
    create_directory(services_path)
    
    # services/games/
    services_games_path = os.path.join(services_path, "games")
    create_directory(services_games_path)
    services_games_files = ["base_game_service.py", "game_service.py"]
    for file in services_games_files:
        create_file(os.path.join(services_games_path, file))
    
    # services/analytics/
    services_analytics_path = os.path.join(services_path, "analytics")
    create_directory(services_analytics_path)
    services_analytics_files = ["analytics_service.py", "report_service.py"]
    for file in services_analytics_files:
        create_file(os.path.join(services_analytics_path, file))
    
    # services/
    services_files = [
        "sessions_service.py",
        "users_service.py",
        "cv_service.py"
    ]
    for file in services_files:
        create_file(os.path.join(services_path, file))

    # analytics/
    analytics_path = os.path.join(base_path, "analytics")
    create_directory(analytics_path)
 

    # utils/
    utils_path = os.path.join(base_path, "utils")
    create_directory(utils_path)
    utils_files = ["logging.py", "monitoring.py", "sync_manager.py"]
    for file in utils_files:
        create_file(os.path.join(utils_path, file))

if __name__ == "__main__":
    generate_project_structure()
    print("Project structure generated successfully!")