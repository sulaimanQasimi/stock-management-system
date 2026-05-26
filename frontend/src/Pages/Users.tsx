import { Link } from '@inertiajs/react';

type User = {
  id: number;
  username: string;
  email: string;
};

const Users = ({ users }: { users: User[] }) => (
  <>
    {users.map((user) => (
      <div key={user.id}>
        <Link href={`/users/${user.id}`}>{user.username}</Link>
        <p>{user.email}</p>
      </div>
    ))}
  </>
);

export default Users;
