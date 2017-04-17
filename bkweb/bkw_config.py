__author__ = 'tok'


class Configuration(object):
    def get_config(self, param, default):
        pass

    def set_config(self, key, value):
        """
        Write to config file.
        """
        assert isinstance(key, str)
        assert isinstance(value, str)
        # Raise error if key contains equals(=)
        assert '=' not in key, "key contains ="
        # Read file if required
        self._parse_if_needed()
        # Update the cache
        self._cache[key.lower().strip()] = value