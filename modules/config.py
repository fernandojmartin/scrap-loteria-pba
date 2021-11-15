from dotenv import dotenv_values
from dataclasses import dataclass


@dataclass
class Config:
    tracking_enabled: bool
    search_url: str
    files_url: str
    date_query_param: str
    throttle_secs: int
    downloads_dir: str


def parse_config() -> Config:
    env = dotenv_values('.env')

    return Config(
        files_url=env['FILES_URL'],
        search_url=env['SEARCH_URL'],
        date_query_param=env['QUERY_PARAM'],
        tracking_enabled=True if env['TRACK_PROCESSED'].lower() == 'true' else False,
        throttle_secs=1,
        downloads_dir=env['DOWNLOADS_DIR'],
    )
