// lib/widgets/custom_button.dart
import 'package:flutter/material.dart';
import '../config/constants.dart';

class CustomButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool loading;
  final IconData? icon;
  final bool outlined;

  const CustomButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.loading = false,
    this.icon,
    this.outlined = false,
  });

  @override
  State<CustomButton> createState() => _CustomButtonState();
}

class _CustomButtonState extends State<CustomButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 100),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.97,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    if (!widget.loading && widget.onPressed != null) {
      _controller.forward();
    }
  }

  void _onTapUp(TapUpDetails details) {
    _controller.reverse();
  }

  void _onTapCancel() {
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final isDisabled = widget.loading || widget.onPressed == null;

    if (widget.outlined) {
      return SizedBox(
        width: double.infinity,
        height: 52,
        child: OutlinedButton(
          onPressed: widget.loading ? null : widget.onPressed,
          style: OutlinedButton.styleFrom(
            foregroundColor: AppColors.deepYellow,
            side: BorderSide(
              color: isDisabled ? AppColors.border : AppColors.deepYellow,
              width: 2,
            ),
            shape: RoundedRectangleBorder(borderRadius: AppRadius.buttonRadius),
            padding: const EdgeInsets.symmetric(vertical: 14),
          ),
          child:
              widget.loading
                  ? const SizedBox(
                    height: 22,
                    width: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation(AppColors.deepYellow),
                    ),
                  )
                  : _buildContent(AppColors.deepYellow),
        ),
      );
    }

    return GestureDetector(
      onTapDown: _onTapDown,
      onTapUp: _onTapUp,
      onTapCancel: _onTapCancel,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(scale: _scaleAnimation.value, child: child);
        },
        child: Container(
          width: double.infinity,
          height: 52,
          decoration: BoxDecoration(
            gradient:
                isDisabled
                    ? const LinearGradient(
                      colors: [Color(0xFFE0E0E0), Color(0xFFD0D0D0)],
                    )
                    : AppColors.yellowGradient,
            borderRadius: AppRadius.buttonRadius,
            boxShadow: isDisabled ? null : AppShadows.button,
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: widget.loading ? null : widget.onPressed,
              borderRadius: AppRadius.buttonRadius,
              splashColor: Colors.white24,
              highlightColor: Colors.white10,
              child: Center(
                child:
                    widget.loading
                        ? const SizedBox(
                          height: 22,
                          width: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            valueColor: AlwaysStoppedAnimation(
                              AppColors.textPrimary,
                            ),
                          ),
                        )
                        : _buildContent(AppColors.textPrimary),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildContent(Color color) {
    if (widget.icon != null) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(widget.icon, size: 20, color: color),
          const SizedBox(width: 8),
          Text(
            widget.text,
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w600,
              color: color,
              letterSpacing: -0.2,
            ),
          ),
        ],
      );
    }

    return Text(
      widget.text,
      style: TextStyle(
        fontSize: 17,
        fontWeight: FontWeight.w600,
        color: color,
        letterSpacing: -0.2,
      ),
    );
  }
}
