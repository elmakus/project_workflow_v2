import tempfile, subprocess, unittest
from pathlib import Path
from tools.pwv22_native_foundation import *

def git(p,*a): return subprocess.check_output(["git","-C",str(p),*a]).decode().strip()

class NativeFoundationTests(unittest.TestCase):
 def fixture(self):
  t=tempfile.TemporaryDirectory(); root=Path(t.name); remote=root/"R.git"; p=root/"work"
  subprocess.check_call(["git","init","--bare","-q",str(remote)])
  subprocess.check_call(["git","clone","-q",str(remote),str(p)])
  subprocess.check_call(["git","-C",str(p),"config","user.email","t@example.invalid"])
  subprocess.check_call(["git","-C",str(p),"config","user.name","T"])
  (p/"a.txt").write_text("alpha\n")
  subprocess.check_call(["git","-C",str(p),"add","a.txt"]); subprocess.check_call(["git","-C",str(p),"commit","-qm","a"])
  c=git(p,"rev-parse","HEAD"); b=git(p,"rev-parse",f"{c}:a.txt")
  subprocess.check_call(["git","-C",str(p),"push","-q","origin","HEAD:refs/heads/main"])
  return t,p,c,b
 def test_exact_identity_and_serving_bytes(self):
  t,p,c,b=self.fixture()
  with t:
   r={"repository":"R","commit":c,"path":"a.txt","blob":b}
   self.assertEqual(exact_blob(p,"R",r,b"alpha\n"),b"alpha\n")
   for k,v in [("repository","X"),("blob","0"*40)]:
    bad=dict(r); bad[k]=v
    with self.assertRaises(NativeFoundationError): exact_blob(p,"R",bad)
   with self.assertRaises(NativeFoundationError): exact_blob(p,"R",r,b"changed\n")
 def test_exact_identity_rejects_unpublished_backslash_and_symlink(self):
  t,p,c,b=self.fixture()
  with t:
   r={"repository":"R","commit":c,"path":"a.txt","blob":b}
   bad=dict(r); bad["path"]="dir\\\\a.txt"
   with self.assertRaises(NativeFoundationError): exact_blob(p,"R",bad)
   (p/"link").symlink_to("a.txt")
   subprocess.check_call(["git","-C",str(p),"add","link"]); subprocess.check_call(["git","-C",str(p),"commit","-qm","symlink"])
   symlink_commit=git(p,"rev-parse","HEAD"); symlink_blob=git(p,"rev-parse",f"{symlink_commit}:link")
   subprocess.check_call(["git","-C",str(p),"push","-q","origin","HEAD:refs/heads/main"])
   link_ref={"repository":"R","commit":symlink_commit,"path":"link","blob":symlink_blob}
   with self.assertRaises(NativeFoundationError): exact_blob(p,"R",link_ref)
   (p/"local.txt").write_text("local\n")
   subprocess.check_call(["git","-C",str(p),"add","local.txt"]); subprocess.check_call(["git","-C",str(p),"commit","-qm","local only"])
   local_commit=git(p,"rev-parse","HEAD"); local_blob=git(p,"rev-parse",f"{local_commit}:local.txt")
   local_ref={"repository":"R","commit":local_commit,"path":"local.txt","blob":local_blob}
   with self.assertRaises(NativeFoundationError): exact_blob(p,"R",local_ref)

 def test_repository_identity_is_derived_from_remote(self):
  t,p,c,b=self.fixture()
  with t:
   r={"repository":"X","commit":c,"path":"a.txt","blob":b}
   with self.assertRaises(NativeFoundationError): exact_blob(p,"X",r)

 def test_material_locality(self):
  r={"repository":"R","commit":"1"*40,"path":"x","blob":"2"*40}
  a=material_fingerprint([r],{"property":"v"})
  self.assertEqual(a,material_fingerprint([r],{"property":"v"}))
  r2=dict(r); r2["blob"]="3"*40
  self.assertNotEqual(a,material_fingerprint([r2],{"property":"v"}))
 def test_native_admission(self):
  official={"official":True,"epoch":"pwv2.2.0","commit":"1"*40}
  self.assertEqual(admit_native({"generation":"pwv2.2-native","epoch":"pwv2.2.0"},official)["epoch"],"pwv2.2.0")
  for state in [{"generation":"v2.1","epoch":"pwv2.2.0"},{"generation":"pwv2.2-native","epoch":"old"},{}]:
   with self.assertRaises(NativeFoundationError): admit_native(state,official)
 def test_guarded_publication_and_race(self):
  head=["1"*40]; writes=[]
  def publish(old,new): self.assertEqual(head[0],old); writes.append((old,new)); head[0]=new
  self.assertEqual(guarded_publish(expected_old="1"*40,candidate="2"*40,read_head=lambda:head[0],publish=publish,readback=lambda:head[0]),"2"*40)
  self.assertEqual(len(writes),1)
  with self.assertRaises(NativeFoundationError): guarded_publish(expected_old="1"*40,candidate="3"*40,read_head=lambda:head[0],publish=publish,readback=lambda:head[0])
  self.assertEqual(len(writes),1)
 def test_readback_failure_is_not_success(self):
  calls=[]
  with self.assertRaises(NativeFoundationError):
   guarded_publish(expected_old="1"*40,candidate="2"*40,read_head=lambda:"1"*40,publish=lambda o,n:calls.append((o,n)),readback=lambda:"1"*40)
  self.assertEqual(len(calls),1)
 def test_atomic_envelope(self):
  self.assertTrue(validate_atomic_candidate({"x":b"1","y":b"2"},{"x","y"}))
  with self.assertRaises(NativeFoundationError): validate_atomic_candidate({"z":b"3"},{"x","y"})
 def test_safe_paths(self):
  for p in ["../x","/x","a/../x","a\\\\b"]:
   with self.assertRaises(NativeFoundationError): safe_path(p)

 def remote_fixture(self):
  t=tempfile.TemporaryDirectory(); root=Path(t.name); remote=root/"remote.git"; a=root/"a"; b=root/"b"
  subprocess.check_call(["git","init","--bare","-q",str(remote)])
  for p in (a,b):
   subprocess.check_call(["git","clone","-q",str(remote),str(p)])
   subprocess.check_call(["git","-C",str(p),"config","user.email","t@example.invalid"])
   subprocess.check_call(["git","-C",str(p),"config","user.name","T"])
  (a/"one").write_text("one\n"); (a/"two").write_text("two\n")
  subprocess.check_call(["git","-C",str(a),"add","one","two"]); subprocess.check_call(["git","-C",str(a),"commit","-qm","base"])
  base=git(a,"rev-parse","HEAD"); subprocess.check_call(["git","-C",str(a),"push","-q","origin","HEAD:refs/heads/main"])
  subprocess.check_call(["git","-C",str(b),"fetch","-q","origin","main"])
  return t,remote,a,b,base
 def test_git_native_atomic_multifile_publish_and_readback(self):
  t,remote,a,b,base=self.remote_fixture()
  with t:
   (a/"one").write_text("ONE\n"); (a/"two").write_text("TWO\n")
   subprocess.check_call(["git","-C",str(a),"add","one","two"]); subprocess.check_call(["git","-C",str(a),"commit","-qm","candidate"])
   candidate=git(a,"rev-parse","HEAD")
   self.assertEqual(guarded_git_ref_publish(repo=a,remote="origin",ref="refs/heads/main",expected_old=base,candidate=candidate),candidate)
   self.assertEqual(remote_ref_head(a,"origin","refs/heads/main"),candidate)
 def test_interleaving_remote_move_rejects_stale_candidate(self):
  t,remote,a,b,base=self.remote_fixture()
  with t:
   (a/"one").write_text("candidate\n"); subprocess.check_call(["git","-C",str(a),"add","one"]); subprocess.check_call(["git","-C",str(a),"commit","-qm","candidate"])
   candidate=git(a,"rev-parse","HEAD")
   subprocess.check_call(["git","-C",str(b),"checkout","-q","-B","main","origin/main"])
   (b/"one").write_text("racer\n"); subprocess.check_call(["git","-C",str(b),"add","one"]); subprocess.check_call(["git","-C",str(b),"commit","-qm","racer"])
   racer=git(b,"rev-parse","HEAD"); subprocess.check_call(["git","-C",str(b),"push","-q","origin","HEAD:refs/heads/main"])
   with self.assertRaises(NativeFoundationError):
    guarded_git_ref_publish(repo=a,remote="origin",ref="refs/heads/main",expected_old=base,candidate=candidate)
   self.assertEqual(remote_ref_head(a,"origin","refs/heads/main"),racer)
 def test_crash_before_atomic_publish_leaves_remote_unchanged(self):
  t,remote,a,b,base=self.remote_fixture()
  with t:
   (a/"one").write_text("candidate\n"); (a/"two").write_text("candidate\n")
   subprocess.check_call(["git","-C",str(a),"add","one","two"]); subprocess.check_call(["git","-C",str(a),"commit","-qm","off-canonical candidate"])
   candidate=git(a,"rev-parse","HEAD")
   self.assertNotEqual(candidate,base)
   self.assertEqual(remote_ref_head(a,"origin","refs/heads/main"),base)

if __name__=="__main__": unittest.main()