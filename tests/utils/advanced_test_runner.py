import time
import json
import sys
import os
from datetime import datetime
from typing import List, Callable, Dict, Any, Optional


class Colors:
    """Códigos de color ANSI para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


class BarStyles:
    """Diferentes estilos de barras de progreso"""
    CLASSIC = {
        'filled': '█',
        'partial': '▌',
        'empty': '░'
    }
    MODERN = {
        'filled': '▓',
        'partial': '▒',
        'empty': '░'
    }
    DOTS = {
        'filled': '●',
        'partial': '◐',
        'empty': '○'
    }
    BLOCKS = {
        'filled': '■',
        'partial': '▣',
        'empty': '□'
    }
    ARROWS = {
        'filled': '▶',
        'partial': '▷',
        'empty': '▷'
    }


class TestConfig:
    """Configuración para el runner de tests"""

    def __init__(self):
        self.bar_style = "modern"  # classic, modern, dots, blocks, arrows
        self.bar_width = 40
        self.show_eta = True
        self.show_individual_times = True
        self.colored_output = True
        self.detailed_summary = True
        self.export_results = False
        self.export_path = "test_results.json"
        self.retry_failed = False
        self.max_retries = 2
        self.silent_mode = False
        self.show_progress_details = True


class TestResult:
    """Resultado de un test individual"""

    def __init__(self, name: str):
        self.name = name
        self.status = "pending"  # pending, running, passed, failed, error
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.error_message = None
        self.response_data = None
        self.retry_count = 0


class AdvancedTestRunner:
    """Runner avanzado para tests con barras de progreso y estadísticas"""

    def __init__(self, module_name: str, config: Optional[TestConfig] = None):
        self.module_name = module_name
        self.config = config or TestConfig()
        self.tests: List[Callable] = []
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        self.total_duration = 0

    def add_test(self, test_function: Callable, name: str = None):
        """Agregar un test al runner"""
        test_name = name or test_function.__name__
        self.tests.append((test_function, test_name))

    def add_tests(self, test_list: List[tuple]):
        """Agregar múltiples tests al runner"""
        for test_func, test_name in test_list:
            self.add_test(test_func, test_name)

    def _get_terminal_width(self) -> int:
        """Obtener ancho del terminal"""
        try:
            return os.get_terminal_size().columns
        except:
            return 80

    def _get_bar_style(self) -> dict:
        """Obtener estilo de barra según configuración"""
        styles = {
            'classic': BarStyles.CLASSIC,
            'modern': BarStyles.MODERN,
            'dots': BarStyles.DOTS,
            'blocks': BarStyles.BLOCKS,
            'arrows': BarStyles.ARROWS
        }
        return styles.get(self.config.bar_style, BarStyles.MODERN)

    def _format_time(self, seconds: float) -> str:
        """Formatear tiempo en formato legible"""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"

    def _calculate_eta(self, current: int, total: int, elapsed: float) -> str:
        """Calcular tiempo estimado restante"""
        if current == 0:
            return "∞"

        avg_time_per_test = elapsed / current
        remaining_tests = total - current
        eta_seconds = avg_time_per_test * remaining_tests

        return self._format_time(eta_seconds)

    def _create_progress_bar(self, current: int, total: int, test_name: str = "",
                             passed: int = 0, failed: int = 0, errors: int = 0,
                             elapsed_time: float = 0) -> str:
        """Crear barra de progreso completa"""

        if not self.config.colored_output:
            # Versión sin colores para CI/CD
            percent = (current / total) * 100
            bar_filled = int(self.config.bar_width * current // total)
            bar = '█' * bar_filled + '░' * (self.config.bar_width - bar_filled)
            return f'[{bar}] {percent:.1f}% | ✓{passed} ✗{failed} ⚠{errors} | {test_name}'

        # Versión con colores
        percent = (current / total) * 100
        bar_filled = int(self.config.bar_width * current // total)

        style = self._get_bar_style()

        # Barra de progreso con colores
        filled_part = f"{Colors.GREEN}{style['filled'] * bar_filled}{Colors.END}"
        empty_part = f"{Colors.GRAY}{style['empty'] * (self.config.bar_width - bar_filled)}{Colors.END}"
        bar = filled_part + empty_part

        # Estadísticas con colores
        stats = (f"{Colors.GREEN}✓{passed}{Colors.END} "
                 f"{Colors.RED}✗{failed}{Colors.END} "
                 f"{Colors.YELLOW}⚠{errors}{Colors.END}")

        # Información adicional
        additional_info = []

        if self.config.show_individual_times and elapsed_time > 0:
            avg_time = elapsed_time / max(current, 1)
            additional_info.append(f"{Colors.CYAN}{self._format_time(avg_time)}/test{Colors.END}")

        if elapsed_time > 0:
            additional_info.append(f"{Colors.BLUE}⏱ {self._format_time(elapsed_time)}{Colors.END}")

        if self.config.show_eta and current > 0 and current < total:
            eta = self._calculate_eta(current, total, elapsed_time)
            additional_info.append(f"{Colors.MAGENTA}ETA: {eta}{Colors.END}")

        # Nombre del test actual
        current_test = f"{Colors.YELLOW}{test_name}{Colors.END}" if test_name else ""

        # Construir línea completa
        info_str = " | ".join(additional_info)
        result = f"[{bar}] {percent:.1f}% | {stats}"

        if info_str:
            result += f" | {info_str}"

        if current_test and self.config.show_progress_details:
            result += f"\n{Colors.DIM}▸ {current_test}{Colors.END}"

        return result

    def _print_header(self):
        """Imprimir encabezado del módulo"""
        if self.config.silent_mode:
            return

        terminal_width = self._get_terminal_width()
        title = f"EJECUTANDO PRUEBAS DEL MÓDULO: {self.module_name.upper()}"

        if self.config.colored_output:
            print(f"\n{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
            print(f"{Colors.BLUE}{'═' * min(len(title), terminal_width)}{Colors.END}")
        else:
            print(f"\n{title}")
            print("=" * min(len(title), terminal_width))

        print(f"📊 Total de pruebas: {len(self.tests)}")
        print(f"🕐 Iniciado: {datetime.now().strftime('%H:%M:%S')}")
        print()

    def _print_progress(self, current: int, test_name: str = ""):
        """Imprimir progreso actual"""
        if self.config.silent_mode:
            return

        elapsed = time.time() - self.start_time if self.start_time else 0
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        errors = sum(1 for r in self.results if r.status == "error")

        progress_bar = self._create_progress_bar(
            current, len(self.tests), test_name, passed, failed, errors, elapsed
        )

        # Limpiar línea y imprimir progreso
        print(f"\r{' ' * self._get_terminal_width()}", end='')
        print(f"\r{progress_bar}", end='', flush=True)

        if self.config.show_progress_details and test_name:
            print()  # Nueva línea para el detalle del test

    def _execute_test(self, test_func: Callable, test_name: str) -> TestResult:
        """Ejecutar un test individual"""
        result = TestResult(test_name)
        result.start_time = time.time()
        result.status = "running"

        try:
            self._print_progress(len([r for r in self.results if r.status != "pending"]),
                                 f"Ejecutando: {test_name}")

            # Ejecutar el test
            test_result = test_func()

            # Determinar resultado
            if test_result is False:
                result.status = "failed"
                result.error_message = "Test retornó False"
            elif test_result is None or test_result is True:
                result.status = "passed"
            else:
                result.status = "passed"
                result.response_data = test_result

        except Exception as e:
            result.status = "error"
            result.error_message = str(e)

        result.end_time = time.time()
        result.duration = result.end_time - result.start_time

        return result

    def _retry_failed_test(self, test_func: Callable, test_name: str,
                           original_result: TestResult) -> TestResult:
        """Reintentar un test fallido"""
        if not self.config.retry_failed or original_result.retry_count >= self.config.max_retries:
            return original_result

        if not self.config.silent_mode:
            print(
                f"\n{Colors.YELLOW}🔄 Reintentando: {test_name} (intento {original_result.retry_count + 2}){Colors.END}")

        time.sleep(1)  # Pequeña pausa antes del reintento

        result = self._execute_test(test_func, test_name)
        result.retry_count = original_result.retry_count + 1

        return result

    def _print_summary(self):
        """Imprimir resumen detallado"""
        if self.config.silent_mode:
            return

        passed = [r for r in self.results if r.status == "passed"]
        failed = [r for r in self.results if r.status == "failed"]
        errors = [r for r in self.results if r.status == "error"]

        total = len(self.results)
        success_rate = (len(passed) / total) * 100 if total > 0 else 0

        print(f"\n\n{Colors.BOLD}🎯 RESUMEN DETALLADO:{Colors.END}")

        if self.config.colored_output:
            print(f"{Colors.BLUE}{'═' * 50}{Colors.END}")
        else:
            print("=" * 50)

        # Estadísticas principales
        print(f"{Colors.GREEN}✅ Pruebas exitosas: {len(passed)}{Colors.END}")
        print(f"{Colors.RED}❌ Pruebas fallidas: {len(failed)}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Pruebas con errores: {len(errors)}{Colors.END}")
        print(f"{Colors.BLUE}⏱️  Tiempo total: {self._format_time(self.total_duration)}{Colors.END}")

        if total > 0:
            avg_time = self.total_duration / total
            print(f"{Colors.CYAN}📊 Promedio por test: {self._format_time(avg_time)}{Colors.END}")

            # Test más rápido y más lento
            if len(passed) > 0:
                fastest = min(passed, key=lambda x: x.duration)
                slowest = max(self.results, key=lambda x: x.duration)

                print(
                    f"{Colors.GREEN}🏆 Test más rápido: {fastest.name} ({self._format_time(fastest.duration)}){Colors.END}")
                print(
                    f"{Colors.MAGENTA}🐌 Test más lento: {slowest.name} ({self._format_time(slowest.duration)}){Colors.END}")

        # Porcentaje de éxito con emoji apropiado
        if success_rate == 100:
            print(f"{Colors.GREEN}🎉 Porcentaje de éxito: {success_rate:.1f}%{Colors.END}")
        elif success_rate >= 80:
            print(f"{Colors.YELLOW}⚠️  Porcentaje de éxito: {success_rate:.1f}%{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Porcentaje de éxito: {success_rate:.1f}%{Colors.END}")

        # Detalles de tests fallidos
        if self.config.detailed_summary and (failed or errors):
            print(f"\n{Colors.RED}❌ TESTS FALLIDOS:{Colors.END}")
            for result in failed + errors:
                status_icon = "💥" if result.status == "error" else "❌"
                print(f"  {status_icon} {result.name}: {result.error_message}")

        # Información adicional
        print(f"\n{Colors.GRAY}🕐 Finalizado: {datetime.now().strftime('%H:%M:%S')}{Colors.END}")

        if self.config.export_results:
            self._export_results()
            print(f"{Colors.CYAN}💾 Resultados exportados a: {self.config.export_path}{Colors.END}")

    def _export_results(self):
        """Exportar resultados a JSON"""
        export_data = {
            "module_name": self.module_name,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "total_duration": self.total_duration,
            "summary": {
                "passed": len([r for r in self.results if r.status == "passed"]),
                "failed": len([r for r in self.results if r.status == "failed"]),
                "errors": len([r for r in self.results if r.status == "error"]),
                "success_rate": (len([r for r in self.results if r.status == "passed"]) / len(self.results)) * 100
            },
            "tests": [
                {
                    "name": r.name,
                    "status": r.status,
                    "duration": r.duration,
                    "error_message": r.error_message,
                    "retry_count": r.retry_count
                }
                for r in self.results
            ]
        }

        with open(self.config.export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def run(self):
        """Ejecutar todos los tests"""
        self._print_header()

        self.start_time = time.time()

        # Inicializar resultados
        self.results = [TestResult(name) for _, name in self.tests]

        # Ejecutar cada test
        for i, (test_func, test_name) in enumerate(self.tests):
            result = self._execute_test(test_func, test_name)

            # Reintentar si falló y está configurado
            if result.status in ["failed", "error"] and self.config.retry_failed:
                result = self._retry_failed_test(test_func, test_name, result)

            self.results[i] = result

            # Pequeña pausa para visualizar el progreso
            if not self.config.silent_mode:
                time.sleep(0.1)

        self.end_time = time.time()
        self.total_duration = self.end_time - self.start_time

        # Limpiar línea de progreso
        if not self.config.silent_mode:
            print(f"\r{' ' * self._get_terminal_width()}")

        self._print_summary()

        return {
            "success": len([r for r in self.results if r.status == "passed"]) == len(self.results),
            "total": len(self.results),
            "passed": len([r for r in self.results if r.status == "passed"]),
            "failed": len([r for r in self.results if r.status == "failed"]),
            "errors": len([r for r in self.results if r.status == "error"]),
            "duration": self.total_duration,
            "results": self.results
        }