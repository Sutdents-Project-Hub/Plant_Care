import 'package:flutter/material.dart';
import '../config/constants.dart';

class AppLogo extends StatelessWidget {
  final double size;

  const AppLogo({super.key, required this.size});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: ClipOval(
        child: Image.asset(
          AppAssets.appIcon,
          fit: BoxFit.cover,
        ),
      ),
    );
  }
}
