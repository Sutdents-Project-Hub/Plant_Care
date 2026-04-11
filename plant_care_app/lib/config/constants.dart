// lib/config/constants.dart
import 'package:flutter/material.dart';

class AppAssets {
  static const String appIcon = 'assets/icon/app_icon.png';
}

class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static const String apiV1BaseUrl = '$apiBaseUrl/api/v1';

  static const String baseUrl = '$apiV1BaseUrl/auth';
  static const String pswBaseUrl = '$apiV1BaseUrl/auth';
  static const String homepageBaseUrl = '$apiV1BaseUrl/homepage';
  static const String plantBaseUrl = '$apiV1BaseUrl/plant';
  static const String aiBaseUrl = '$apiV1BaseUrl/ai';
}

class AppText {
  static const title = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    letterSpacing: -0.5,
  );

  static const subtitle = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w500,
    color: Color(0xFF666666),
  );

  static const sectionTitle = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.3,
  );

  static const cardTitle = TextStyle(fontSize: 20, fontWeight: FontWeight.w700);

  static const body = TextStyle(fontSize: 14, height: 1.5);
}

class AppColors {
  // 主色系 - 黃色
  static const primaryYellow = Color(0xFFFFD54F); // 溫和黃
  static const deepYellow = Color(0xFFFBC02D); // 深黃
  static const lightYellow = Color(0xFFFFF8E1); // 淺黃背景
  static const amberAccent = Color(0xFFFFAB00); // 琥珀強調色

  // 漸層
  static const yellowGradient = LinearGradient(
    colors: [primaryYellow, deepYellow],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const warmGradient = LinearGradient(
    colors: [Color(0xFFFFE082), Color(0xFFFFCA28)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  // 背景色
  static const scaffoldBg = Color(0xFFFAFAFA);
  static const cardBg = Colors.white;
  static const surfaceBg = Color(0xFFF5F5F5);

  // 狀態色
  static const success = Color(0xFF4CAF50);
  static const successLight = Color(0xFFE8F5E9);
  static const warning = Color(0xFFFF9800);
  static const warningLight = Color(0xFFFFF3E0);
  static const error = Color(0xFFE53935);
  static const errorLight = Color(0xFFFFEBEE);

  // 文字色
  static const textPrimary = Color(0xFF212121);
  static const textSecondary = Color(0xFF757575);
  static const textHint = Color(0xFFBDBDBD);

  // 邊框色
  static const border = Color(0xFFE0E0E0);
  static const borderLight = Color(0xFFF0F0F0);

  // 分隔線
  static const divider = Color(0xFFEEEEEE);
}

class AppShadows {
  static const card = [
    BoxShadow(color: Color(0x0A000000), blurRadius: 8, offset: Offset(0, 2)),
    BoxShadow(color: Color(0x05000000), blurRadius: 20, offset: Offset(0, 4)),
  ];

  static const elevated = [
    BoxShadow(color: Color(0x15000000), blurRadius: 12, offset: Offset(0, 4)),
    BoxShadow(color: Color(0x08000000), blurRadius: 24, offset: Offset(0, 8)),
  ];

  static const button = [
    BoxShadow(color: Color(0x30FBC02D), blurRadius: 12, offset: Offset(0, 4)),
  ];

  static const soft = [
    BoxShadow(color: Color(0x08000000), blurRadius: 6, offset: Offset(0, 2)),
  ];
}

class AppRadius {
  static const double xs = 6;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double xxl = 28;

  static final cardRadius = BorderRadius.circular(md);
  static final buttonRadius = BorderRadius.circular(md);
  static final inputRadius = BorderRadius.circular(md);
  static final sheetRadius = const BorderRadius.vertical(
    top: Radius.circular(xl),
  );
}

class AppSpacing {
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double xxl = 24;
  static const double xxxl = 32;

  static const pagePadding = EdgeInsets.all(xl);
  static const cardPadding = EdgeInsets.all(lg);
  static const sectionSpacing = SizedBox(height: lg);
}
