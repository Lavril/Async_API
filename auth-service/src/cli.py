import asyncio
import typer
from rich import print

from db.postgres import async_session
from db.repository import UserRepository

cli = typer.Typer()


@cli.command()
def createsuperuser(
    login: str = typer.Option(..., "--login", "-l", help="Login name"),
    email: str = typer.Option(..., "--email", "-e", help="Email address"),
    first_name: str = typer.Option(..., "--first-name", "-f", help="First name"),
    last_name: str = typer.Option(..., "--last-name", "-s", help="Last name"),
    password: str = typer.Option(..., "--password", "-p", help="Password")
):
    """Create superuser with all permissions"""
    
    async def _run():
        async with async_session() as session:
            from services.role_service import RoleService
            role_service = RoleService(session)
            await role_service.initialize_default_roles()
            
            user_repo = UserRepository(session)

            existing_user = await user_repo.get_user_by_login(login)
            if existing_user:
                print("❌ Login already registered")
                return

            existing_email = await user_repo.get_user_by_email(email)
            if existing_email:
                print("❌ Email already registered")
                return

            await user_repo.create_user(
                login=login,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role_name="superuser"
            )
            print("✅ Superuser created with 'superuser' role")

    asyncio.run(_run())


@cli.command()
def listroles():
    """List all available roles in the system"""
    
    async def _run():
        async with async_session() as session:
            from services.role_service import RoleService
            role_service = RoleService(session)

            await role_service.initialize_default_roles()

            from db.role_repository import RoleTypeRepository
            role_type_repo = RoleTypeRepository(session)
            roles = await role_type_repo.get_all_roles()
            
            if not roles:
                print("❌ No roles found in database")
                return
                
            print("\n📋 Available roles:")
            print("-" * 50)
            for role in roles:
                from constants.permissions import RolePermissions
                permissions_list = RolePermissions.get_permissions_list(role.permissions)
                print(f"{role.name} (priority: {role.priority})")
                print(f"{role.description}")
                print(f"Permissions: {', '.join(permissions_list) if permissions_list else 'None'}")
                print()
    
    asyncio.run(_run())


@cli.command()
def createuser(
    login: str = typer.Option(..., "--login", "-l", help="Login name"),
    email: str = typer.Option(..., "--email", "-e", help="Email address"),
    first_name: str = typer.Option(..., "--first-name", "-f", help="First name"),
    last_name: str = typer.Option(..., "--last-name", "-s", help="Last name"),
    password: str = typer.Option(..., "--password", "-p", help="Password"),
    role: str = typer.Option("user", "--role", "-r", help="Role name (default: user)")
):
    """Create user with specific role"""
    
    async def _run():
        async with async_session() as session:
            from services.role_service import RoleService
            role_service = RoleService(session)
            await role_service.initialize_default_roles()

            from db.role_repository import RoleTypeRepository
            role_type_repo = RoleTypeRepository(session)
            available_roles = await role_type_repo.get_all_roles()
            
            if not available_roles:
                print("❌ No roles available. Please initialize roles first.")
                return
                
            role_names = [role.name for role in available_roles]
            
            if role not in role_names:
                print(f"❌ Role '{role}' not available. Choose from: {', '.join(role_names)}")
                return
            
            user_repo = UserRepository(session)

            existing_user = await user_repo.get_user_by_login(login)
            if existing_user:
                print("❌ Login already registered")
                return

            existing_email = await user_repo.get_user_by_email(email)
            if existing_email:
                print("❌ Email already registered")
                return

            await user_repo.create_user(
                login=login,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role_name=role
            )
            print(f"✅ User '{login}' created with role '{role}'")
    
    asyncio.run(_run())


if __name__ == "__main__":
    cli()
