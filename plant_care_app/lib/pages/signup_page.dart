import 'package:flutter/material.dart';
import '../config/constants.dart';
import '../services/api_service.dart';
import '../utils/tools.dart';
import '../widgets/custom_button.dart';
import '../widgets/custom_text_field.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final _form = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  final _birthdayCtrl = TextEditingController();
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  bool _loading = false;

  DateTime? _birthday;

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _phone.dispose();
    _birthdayCtrl.dispose();
    _password.dispose();
    _confirm.dispose();
    super.dispose();
  }

  Future<void> _pickBirthday() async {
    final today = DateTime.now();
    final initial =
        _birthday ?? DateTime(today.year - 18, today.month, today.day);
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(1900),
      lastDate: today,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: AppColors.deepYellow,
              onPrimary: AppColors.textPrimary,
              surface: AppColors.cardBg,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        _birthday = picked;
        _birthdayCtrl.text = ymd(picked);
      });
    }
  }

  Future<void> _onSignup() async {
    if (!_form.currentState!.validate()) return;
    if (_birthday == null) {
      await showAlert(
        context,
        'Please select your birthday',
        title: 'Incomplete Form',
      );
      return;
    }

    setState(() => _loading = true);
    try {
      await ApiService.signup(
        name: _name.text.trim(),
        email: _email.text.trim(),
        password: _password.text,
        phone: _phone.text.trim(),
        birthday: _birthdayCtrl.text,
      );
      if (!mounted) return;
      await showAlert(
        context,
        'Registration successful',
        title: 'Sign Up Successful',
      );
      if (!mounted) return;
      Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      await showAlert(context, e.toString(), title: 'Sign Up Failed');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 背景裝飾
          Positioned(
            top: -80,
            left: -60,
            child: Container(
              width: 220,
              height: 220,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.primaryYellow.withAlpha(89),
                    AppColors.primaryYellow.withAlpha(0),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: -60,
            right: -40,
            child: Container(
              width: 180,
              height: 180,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppColors.deepYellow.withAlpha(64),
                    AppColors.deepYellow.withAlpha(0),
                  ],
                ),
              ),
            ),
          ),

          // 主內容
          SafeArea(
            child: Column(
              children: [
                // 返回按鈕
                Align(
                  alignment: Alignment.centerLeft,
                  child: Padding(
                    padding: const EdgeInsets.only(left: 8, top: 8),
                    child: IconButton(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Icons.arrow_back_ios_new_rounded),
                      style: IconButton.styleFrom(
                        backgroundColor: AppColors.cardBg,
                        padding: const EdgeInsets.all(12),
                      ),
                    ),
                  ),
                ),

                // 表單
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 400),
                      child: Form(
                        key: _form,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // 標題
                            Text(
                              'Create Account',
                              style: AppText.title.copyWith(
                                color: AppColors.textPrimary,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Start your plant care journey today',
                              style: AppText.subtitle,
                              textAlign: TextAlign.center,
                            ),

                            const SizedBox(height: 32),

                            // 輸入框
                            CustomTextField(
                              controller: _name,
                              label: 'Full Name',
                              prefixIcon: Icons.person_outline,
                              validator:
                                  (v) =>
                                      requiredValidator(v, label: 'Full Name'),
                            ),
                            const SizedBox(height: 16),

                            CustomTextField(
                              controller: _email,
                              label: 'Email',
                              prefixIcon: Icons.email_outlined,
                              keyboardType: TextInputType.emailAddress,
                              validator: emailValidator,
                            ),
                            const SizedBox(height: 16),

                            CustomTextField(
                              controller: _phone,
                              label: 'Phone',
                              prefixIcon: Icons.phone_outlined,
                              keyboardType: TextInputType.phone,
                              validator:
                                  (v) => requiredValidator(v, label: 'Phone'),
                            ),
                            const SizedBox(height: 16),

                            // 生日選擇
                            GestureDetector(
                              onTap: _pickBirthday,
                              child: AbsorbPointer(
                                child: CustomTextField(
                                  controller: _birthdayCtrl,
                                  label: 'Birthday',
                                  prefixIcon: Icons.cake_outlined,
                                  hintText: 'Tap to select',
                                  readOnly: true,
                                  suffixIcon: Icon(
                                    Icons.calendar_today_outlined,
                                    color: AppColors.textSecondary,
                                    size: 20,
                                  ),
                                  validator:
                                      (v) => requiredValidator(
                                        v,
                                        label: 'Birthday',
                                      ),
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),

                            CustomTextField(
                              controller: _password,
                              label: 'Password',
                              prefixIcon: Icons.lock_outline,
                              obscureText: true,
                              validator: passwordValidator,
                            ),
                            const SizedBox(height: 16),

                            CustomTextField(
                              controller: _confirm,
                              label: 'Confirm Password',
                              prefixIcon: Icons.lock_outline,
                              obscureText: true,
                              validator:
                                  (v) => confirmPasswordValidator(
                                    v,
                                    _password.text,
                                  ),
                            ),

                            const SizedBox(height: 32),

                            // 註冊按鈕
                            CustomButton(
                              text: 'Create Account',
                              onPressed: _onSignup,
                              loading: _loading,
                            ),

                            const SizedBox(height: 16),

                            // 返回登入
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  'Already have an account? ',
                                  style: TextStyle(
                                    color: AppColors.textSecondary,
                                    fontSize: 14,
                                  ),
                                ),
                                GestureDetector(
                                  onTap: () => Navigator.of(context).pop(),
                                  child: Text(
                                    'Sign In',
                                    style: TextStyle(
                                      color: AppColors.deepYellow,
                                      fontSize: 14,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
