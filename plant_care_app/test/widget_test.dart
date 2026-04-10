// 基本 Flutter widget 測試
// 驗證 PlantAPP 可正常啟動並顯示 loading indicator

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:plant/main.dart';

void main() {
  testWidgets('App 啟動時顯示 loading indicator', (WidgetTester tester) async {
    // 建立 APP 並觸發一幀
    await tester.pumpWidget(const MyApp());

    // 驗證 LaunchGate 顯示 CircularProgressIndicator
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
