import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import '../config/constants.dart';
import '../services/api_service.dart';
import '../utils/session.dart';
import '../utils/tools.dart';
import '../widgets/app_logo.dart';
import '../widgets/custom_button.dart';
import '../widgets/custom_text_field.dart';
import 'signup_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _form = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _loading = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _onLogin() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await ApiService.login(
        email: _email.text.trim(),
        password: _password.text,
      );
      if (!mounted) return;
      final next = Session.mustChangePassword ? '/force_change_password' : '/home';
      Navigator.pushReplacementNamed(context, next);
    } catch (e) {
      final msg = e is ApiException ? e.message : e.toString();
      await showAlert(context, msg, title: 'Login Failed');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<String?> _promptEmail() async {
    final controller = TextEditingController(text: _email.text.trim());
    String? errorText;

    final result = await showDialog<String?>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setState) {
            return AlertDialog(
              title: const Text('Forgot Password'),
              content: TextField(
                controller: controller,
                keyboardType: TextInputType.emailAddress,
                decoration: InputDecoration(
                  labelText: 'Email',
                  errorText: errorText,
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(ctx).pop(null),
                  child: const Text('Cancel'),
                ),
                TextButton(
                  onPressed: () {
                    final value = controller.text.trim();
                    final err = emailValidator(value);
                    if (err != null) {
                      setState(() => errorText = err);
                      return;
                    }
                    Navigator.of(ctx).pop(value);
                  },
                  child: const Text('OK'),
                ),
              ],
            );
          },
        );
      },
    );

    controller.dispose();
    return result;
  }

  Future<void> _onForgotPassword() async {
    final email = await _promptEmail();
    if (email == null) return;
    if (!mounted) return;

    try {
      final res = await ApiService.forgotPassword(email: email);
      if (!mounted) return;

      await showAlert(
        context,
        res['message']?.toString() ??
            'If the account exists, a reset email will be sent.',
        title: 'Password Reset',
      );
    } catch (e) {
      if (!mounted) return;
      final msg = e is ApiException ? e.message : e.toString();
      await showAlert(context, msg, title: 'Reset Failed');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 背景裝飾
          Positioned(
            top: -100,
            right: -80,
            child: Container(
              width: 280,
              height: 280,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.primaryYellow.withAlpha(102),
                    AppColors.primaryYellow.withAlpha(0),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            top: 60,
            left: -60,
            child: Container(
              width: 180,
              height: 180,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.deepYellow.withAlpha(77),
                    AppColors.deepYellow.withAlpha(0),
                  ],
                ),
              ),
            ),
          ),

          // 主內容
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 400),
                  child: Form(
                    key: _form,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // 植物圖標
                        const SizedBox(height: 12),
                        Center(
                          child: Padding(
                            padding: const EdgeInsets.only(bottom: 24),
                            child: Container(
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: AppColors.deepYellow.withAlpha(70),
                                    blurRadius: 28,
                                    spreadRadius: 2,
                                    offset: Offset.zero,
                                  ),
                                  BoxShadow(
                                    color: AppColors.primaryYellow.withAlpha(
                                      50,
                                    ),
                                    blurRadius: 42,
                                    spreadRadius: 8,
                                    offset: Offset.zero,
                                  ),
                                ],
                              ),
                              child: const AppLogo(size: 92),
                            ),
                          ),
                        ),

                        // 標題
                        Text(
                          'Welcome Back',
                          style: AppText.title.copyWith(
                            color: AppColors.textPrimary,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Sign in to continue caring for your plants',
                          style: AppText.subtitle,
                          textAlign: TextAlign.center,
                        ),

                        const SizedBox(height: 40),

                        // 輸入框
                        CustomTextField(
                          controller: _email,
                          label: 'Email',
                          prefixIcon: Icons.email_outlined,
                          keyboardType: TextInputType.emailAddress,
                          validator: emailValidator,
                        ),
                        const SizedBox(height: 16),
                        CustomTextField(
                          controller: _password,
                          label: 'Password',
                          prefixIcon: Icons.lock_outline,
                          obscureText: true,
                          validator: passwordValidator,
                        ),

                        const SizedBox(height: 12),

                        // 忘記密碼
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: _onForgotPassword,
                            style: TextButton.styleFrom(
                              padding: EdgeInsets.zero,
                              minimumSize: Size.zero,
                              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                            child: Text(
                              'Forgot password?',
                              style: TextStyle(
                                color: AppColors.textSecondary,
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 24),

                        // 登入按鈕
                        CustomButton(
                          text: 'Sign In',
                          onPressed: _onLogin,
                          loading: _loading,
                        ),

                        const SizedBox(height: 24),

                        // 分隔線
                        Row(
                          children: [
                            Expanded(
                              child: Container(
                                height: 1,
                                color: AppColors.border,
                              ),
                            ),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              child: Text(
                                'or',
                                style: TextStyle(
                                  color: AppColors.textSecondary,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                            Expanded(
                              child: Container(
                                height: 1,
                                color: AppColors.border,
                              ),
                            ),
                          ],
                        ),

                        const SizedBox(height: 24),

                        // 註冊按鈕
                        CustomButton(
                          text: 'Create Account',
                          outlined: true,
                          onPressed: () {
                            Navigator.of(context).push(
                              CupertinoPageRoute(
                                builder: (_) => const SignupPage(),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
