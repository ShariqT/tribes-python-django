from tribes_core.lib.actions import generate_pems, check_for_pems
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def make_member_A(self):
        path = "./member_A_keys/"
        if check_for_pems(path) is False:
            generate_pems(path)

    def make_member_B(self):
        path = './member_B_keys/'
        if check_for_pems(path) is False:
            generate_pems(path)

    def make_member_C(self):
        path = './member_C_keys/'
        if check_for_pems(path) is False:
            generate_pems(path)

    def handle(self, *args, **options):
        self.make_member_A()
        self.make_member_B()
        self.make_member_C()
        self.stdout.write(self.style.SUCCESS('Done!'))