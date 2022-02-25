import os
from api_flow.config import Config
from api_flow.complex_namespace import ComplexNamespace


class Profiles(ComplexNamespace):
    def __init__(self, profile=None, profiles=None):
        super().__init__()
        """
        Constructor for Profiles.        
        :argument profile: An optional convenience argument for a singular
                          profile equivalent to "profiles=['profile_name']".
        :type profile: str | None
        :param profiles: An optional list of strings giving the base name of
                         "profile" yaml files that provide base configuration
                         data. These files must resolve as dicts at the top
                         level. They will be loaded in order and merged into
                         the context, with duplicate keys resolved in favor
                         of the last file defining it. Directories are
                         supported and can be used to categorize types of
                         configuration, e.g., ['environment/test', 'site/main']
        :type profiles: list[str] | str | None
        """
        self._profiles = self._get_profiles(profile, profiles)
        self._load_profiles()

    @staticmethod
    def _get_profiles(profile, profiles):
        all_profiles = [] if profiles is None else profiles
        all_profiles = [all_profiles] if not isinstance(all_profiles, list) else all_profiles
        if profile is not None:
            all_profiles.append(profile)
        return all_profiles

    def _load_profiles(self):
        if len(self._profiles) > 0:
            print(f'Loading {str(self._profiles)} from {Config.profile_path}')
            for profile in self._profiles:
                self.merge(self.from_yaml(os.path.join(
                    Config.profile_path,
                    f'{profile}.yaml'
                )))
