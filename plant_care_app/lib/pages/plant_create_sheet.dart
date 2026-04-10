// lib/pages/plant_create_sheet.dart
import 'package:flutter/material.dart';
import '../config/constants.dart';
import '../services/api_service.dart';
import '../utils/session.dart';
import '../utils/tools.dart';
import '../widgets/custom_button.dart';
import 'package:url_launcher/url_launcher.dart';

class PlantCreateSheet extends StatefulWidget {
  const PlantCreateSheet({super.key});

  @override
  State<PlantCreateSheet> createState() => _PlantCreateSheetState();
}

class _PlantCreateSheetState extends State<PlantCreateSheet> {
  final _form = GlobalKey<FormState>();
  final _variety = TextEditingController();
  final _name = TextEditingController();
  String _state = 'seedling';
  bool _loading = false;

  static final Uri _plantNetUrl = Uri.parse(
    'https://identify.plantnet.org/zh-tw',
  );

  @override
  void dispose() {
    _variety.dispose();
    _name.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_form.currentState!.validate()) return;

    if (!Session.isLoggedIn) {
      await showAlert(context, 'Please sign in again.', title: 'No session');
      return;
    }

    setState(() => _loading = true);
    try {
      final today = ymd(DateTime.now());
      await ApiService.createPlant(
        plantVariety: _variety.text.trim(),
        plantName: _name.text.trim(),
        plantState: _state,
        setupTime: today,
      );

      if (!mounted) return;
      Navigator.of(context).pop(true);
    } catch (e) {
      await showAlert(context, e.toString(), title: 'Create Failed');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _openPlantNet() async {
    final ok = await launchUrl(
      _plantNetUrl,
      mode: LaunchMode.externalApplication,
    );
    if (!ok && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Failed to open link')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.cardBg,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Padding(
        padding: EdgeInsets.only(
          left: 24,
          right: 24,
          top: 12,
          bottom: bottomInset + 24,
        ),
        child: SafeArea(
          top: false,
          child: SingleChildScrollView(
            child: Form(
              key: _form,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 拖拉指示器
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      margin: const EdgeInsets.only(bottom: 20),
                      decoration: BoxDecoration(
                        color: AppColors.border,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),

                  // 標題
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          gradient: AppColors.yellowGradient,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.add_rounded,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Add New Plant',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          SizedBox(height: 2),
                          Text(
                            'Start tracking your plant',
                            style: TextStyle(
                              fontSize: 13,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Plant variety
                  _buildInputLabel(
                    'Plant Variety',
                    Icons.local_florist_outlined,
                  ),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _variety,
                    decoration: InputDecoration(
                      hintText: 'e.g., Monstera Deliciosa',
                      hintStyle: const TextStyle(color: AppColors.textHint),
                    ),
                    validator:
                        (v) =>
                            (v == null || v.trim().isEmpty)
                                ? 'Please enter variety'
                                : null,
                  ),

                  // PlantNet 連結
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton.icon(
                      onPressed: _openPlantNet,
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      icon: const Icon(
                        Icons.camera_alt_outlined,
                        size: 16,
                        color: AppColors.deepYellow,
                      ),
                      label: const Text(
                        'Identify by photo',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.deepYellow,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Plant name
                  _buildInputLabel('Plant Nickname', Icons.badge_outlined),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _name,
                    decoration: InputDecoration(
                      hintText: 'Give your plant a name',
                      hintStyle: const TextStyle(color: AppColors.textHint),
                    ),
                    validator:
                        (v) =>
                            (v == null || v.trim().isEmpty)
                                ? 'Please enter name'
                                : null,
                  ),

                  const SizedBox(height: 20),

                  // Plant state
                  _buildInputLabel('Growth Stage', Icons.spa_outlined),
                  const SizedBox(height: 8),
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.cardBg,
                      borderRadius: AppRadius.inputRadius,
                      border: Border.all(color: AppColors.border),
                    ),
                    child: DropdownButtonFormField<String>(
                      initialValue: _state,
                      onChanged: (v) => setState(() => _state = v ?? _state),
                      items: const [
                        DropdownMenuItem(
                          value: 'seedling',
                          child: Text('🌱 Seedling'),
                        ),
                        DropdownMenuItem(
                          value: 'growing',
                          child: Text('🌿 Growing'),
                        ),
                        DropdownMenuItem(
                          value: 'stable',
                          child: Text('🌳 Stable'),
                        ),
                      ],
                      decoration: const InputDecoration(
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(
                          vertical: 14,
                          horizontal: 16,
                        ),
                      ),
                      style: const TextStyle(
                        fontSize: 16,
                        color: AppColors.textPrimary,
                      ),
                      dropdownColor: AppColors.cardBg,
                      isDense: true,
                      icon: const Icon(Icons.keyboard_arrow_down_rounded),
                    ),
                  ),

                  const SizedBox(height: 28),

                  // Submit
                  CustomButton(
                    text: 'Add Plant',
                    icon: Icons.eco_rounded,
                    onPressed: _submit,
                    loading: _loading,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInputLabel(String label, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: 6),
        Text(
          label,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }
}
