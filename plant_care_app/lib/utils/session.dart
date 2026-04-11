import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class Session {
  static const _kEmailKey = 'user_email';
  static const _kNameKey = 'user_name';
  static const _kPointsKey = 'user_points';
  static const _kAccessTokenKey = 'access_token';
  static const _kRefreshTokenKey = 'refresh_token';
  static const _kAccessExpiresAtKey = 'access_expires_at';

  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  static String? _email;
  static String? _name;
  static int _points = 0;
  static String? _accessToken;
  static String? _refreshToken;
  static DateTime? _accessExpiresAt;
  static bool _ready = false;

  static String? get email => _email;
  static String? get name => _name;
  static int get points => _points;
  static String? get accessToken => _accessToken;
  static String? get refreshToken => _refreshToken;
  static DateTime? get accessExpiresAt => _accessExpiresAt;
  static bool get isReady => _ready;
  static bool get isLoggedIn => (_refreshToken ?? '').isNotEmpty;

  static Future<void> init() async {
    _email = await _storage.read(key: _kEmailKey);
    _name = await _storage.read(key: _kNameKey);
    final pointsRaw = await _storage.read(key: _kPointsKey);
    _points = int.tryParse((pointsRaw ?? '').trim()) ?? 0;
    _accessToken = await _storage.read(key: _kAccessTokenKey);
    _refreshToken = await _storage.read(key: _kRefreshTokenKey);
    final expiresAtRaw = await _storage.read(key: _kAccessExpiresAtKey);
    _accessExpiresAt = expiresAtRaw == null ? null : DateTime.tryParse(expiresAtRaw);
    _ready = true;
  }

  static Future<void> setAuth({
    required String email,
    required String accessToken,
    required String refreshToken,
    required DateTime accessExpiresAt,
    String? name,
    int? points,
  }) async {
    _email = email;
    _name = name;
    _points = points ?? _points;
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    _accessExpiresAt = accessExpiresAt;

    await _storage.write(key: _kEmailKey, value: email);
    await _storage.write(key: _kNameKey, value: name);
    await _storage.write(key: _kPointsKey, value: _points.toString());
    await _storage.write(key: _kAccessTokenKey, value: accessToken);
    await _storage.write(key: _kRefreshTokenKey, value: refreshToken);
    await _storage.write(key: _kAccessExpiresAtKey, value: accessExpiresAt.toIso8601String());
  }

  static Future<void> setTokens({
    required String accessToken,
    required String refreshToken,
    required DateTime accessExpiresAt,
  }) async {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    _accessExpiresAt = accessExpiresAt;

    await _storage.write(key: _kAccessTokenKey, value: accessToken);
    await _storage.write(key: _kRefreshTokenKey, value: refreshToken);
    await _storage.write(key: _kAccessExpiresAtKey, value: accessExpiresAt.toIso8601String());
  }

  static Future<void> setUserInfo({String? email, String? name, int? points}) async {
    if (email != null) {
      _email = email;
      await _storage.write(key: _kEmailKey, value: email);
    }
    if (name != null) {
      _name = name;
      await _storage.write(key: _kNameKey, value: name);
    }
    if (points != null) {
      _points = points;
      await _storage.write(key: _kPointsKey, value: points.toString());
    }
  }

  static Future<void> clear() async {
    _email = null;
    _name = null;
    _points = 0;
    _accessToken = null;
    _refreshToken = null;
    _accessExpiresAt = null;
    await _storage.delete(key: _kEmailKey);
    await _storage.delete(key: _kNameKey);
    await _storage.delete(key: _kPointsKey);
    await _storage.delete(key: _kAccessTokenKey);
    await _storage.delete(key: _kRefreshTokenKey);
    await _storage.delete(key: _kAccessExpiresAtKey);
  }
}
