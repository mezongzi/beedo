# coding=utf8
from __future__ import absolute_import

import os
import yaml
from models import Entry


def load_config(app, config_name='config.py'):
    app.config.from_pyfile(config_name)
    app.config.setdefault('DEBUG', False)
    app.config.setdefault('HOST', '0.0.0.0')
    app.config.setdefault('PORT', 5500)

    app.config.setdefault('LOGS_DIR', 'logs')
    app.config.setdefault('DATA_DIR', 'content')
    app.config.setdefault('LANGUAGES_DIR', 'languages')

    app.config.setdefault('DATA_FILE_EXT', '.md')
    app.config.setdefault('LOCALE', 'en')

    app.config.setdefault('WX_TOKEN', u'token')
    app.config.setdefault('APP_ID', u'')
    app.config.setdefault('ENCODING_AES_KEY', u'')

    app.config.setdefault('DEFAULT_MESSAGE', u'...')


def watch_files_date(app):
    print '----------- Watch modification -----------'
    content_dir = app.config.get('DATA_DIR')

    all_files = _all_file_paths(app)
    files_modified = {}

    for f in all_files:
        if _is_invisible(f, content_dir):
            continue
        file_id = os.path.splitext(os.path.basename(f))[0]
        try:
            f_mtime = os.path.getmtime(f)
        except OSError:
            f_mtime = 0
        files_modified[f] = {
            '_id': file_id,
            'modified': f_mtime
        }
    return files_modified


def load_files(app):
    print '----------- Load Files -----------'
    content_dir = app.config.get('DATA_DIR')

    all_files = _all_file_paths(app)
    files_data = {}
    for f in all_files:
        if _is_invisible(f, content_dir):
            print '***', f
            continue

        file_id = os.path.splitext(os.path.basename(f))[0]
        print '-->', f, '=>', file_id

        try:
            files_data[file_id] = _single_file(f, file_id)
        except Exception as e:
            app.logger.error(e)
            continue

    return files_data


def load_single_file(file_path, file_id):
    try:
        return _single_file(file_path, file_id)
    except Exception:
        return None


def load_keys(app, file_data):
    print '----------- Load Keys -----------'
    keys_data = {}
    conflicts = []

    def _log_conflicts(key, fname, another_id):
        conflicts.append('{}: {} >>> {}'.format(key, fname, another_id))

    for fname, f in file_data.iteritems():
        if fname in app.config['STATIC_FILENAME'] or not f.get('status'):
            continue
        for key in f.get('keywords', [])[:60]:
            if not key or not isinstance(key, basestring) or key in keys_data:
                _log_conflicts(key, fname, keys_data.get(key))
            else:
                print '-->', key
                keys_data.update({key: fname})

    print 'Conflicts ------------>'
    for entry in conflicts:
        print entry
    print '<---------------------'
    print '\n'
    return keys_data


# helpers
def _all_file_paths(app):
    content_dir = app.config.get('DATA_DIR')
    content_ext = app.config.get('DATA_FILE_EXT')

    all_files = []
    for root, directory, files in os.walk(content_dir):
        file_full_paths = [
            os.path.join(root, f)
            for f in filter(lambda x: x.endswith(content_ext), files)
        ]
        all_files.extend(file_full_paths)
    return all_files


def _is_invisible(f, content_dir):
    relative_path = f.split(content_dir + '/', 1)[1]
    file_id = os.path.splitext(os.path.basename(f))[0]
    if relative_path.startswith('_') or file_id.startswith('_'):
        return True
    else:
        return False


def _single_file(file_path, file_id):
    try:
        with open(file_path, 'r') as fh:
            meta_string = fh.read().decode('utf-8')
    except Exception as e:
        e.current_file = file_path
        raise e
    try:
        meta = _parse_file_meta(meta_string)
    except Exception as e:
        e.current_file = file_path
        raise e

    items = [_prase_news_item(item) for item in meta.pop('messages', [])]
    _type = meta.pop('type', None)
    if not _type:
        _type = 'news' if items else 'text'
    entry = Entry({
        '_id': file_id,
        'keywords': meta.pop('keywords', meta.pop('keys', [])),
        'type': _type,
        'status': meta.pop('status', 1),
        'text': meta.pop('text', u''),
        'messages': items[:8],  # max 8 entries
    }, file_path)
    return entry


def _prase_news_item(item):
        return {
            'title': item.get('title', u''),
            'description': item.get('description', u''),
            'picurl': item.get('picurl', u''),
            'url': item.get('url', u''),
        }


def _parse_file_meta(meta_string):
    def convert_data_decode(x):
        if isinstance(x, dict):
            return dict((k.lower(), convert_data_decode(v))
                        for k, v in x.iteritems())
        elif isinstance(x, list):
            return list([convert_data_decode(i) for i in x])
        elif isinstance(x, str):
            return x.decode('utf-8')
        elif isinstance(x, (unicode, int, float, bool)) or x is None:
            return x
        else:
            try:
                x = str(x).decode('utf-8')
            except Exception as e:
                print e
                pass
        return x
    yaml_data = yaml.safe_load(meta_string)
    headers = convert_data_decode(yaml_data)
    return headers
