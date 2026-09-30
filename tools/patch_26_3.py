from pathlib import Path
import sys

project = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("project")
root = project / "src" / "main" / "java"

count = 0
for p in root.rglob("*.java"):
    s = p.read_text(encoding="utf-8")
    ns = s.replace("Minecraft.getInstance().setScreen(", "Minecraft.getInstance().gui.setScreen(")
    ns = ns.replace("client.setScreen(", "client.gui.setScreen(")
    if ns != s:
        p.write_text(ns, encoding="utf-8")
        count += 1

for name in ["TxtBrowserScreen.java", "MaterialListScreen.java", "MaterialDetailScreen.java"]:
    p = root / "com" / "litematlist" / "gui" / name
    s = p.read_text(encoding="utf-8")
    s = s.replace("import com.mojang.blaze3d.textures.GpuTextureView;\n", "")
    s = s.replace("import com.mojang.blaze3d.textures.GpuSampler;\n", "")
    s = s.replace("Pair<GpuTextureView, GpuSampler> pair", "var pair")
    p.write_text(s, encoding="utf-8")

p = root / "com" / "litematlist" / "config" / "Configs.java"
s = p.read_text(encoding="utf-8")
s = s.replace("import java.nio.file.Files;\n",
              "import java.nio.file.Files;\n"
              "import java.nio.charset.StandardCharsets;\n"
              "import java.io.Reader;\n"
              "import java.io.Writer;\n")
s = s.replace("import com.google.gson.JsonObject;\n",
              "import com.google.gson.JsonObject;\n"
              "import com.google.gson.JsonParser;\n"
              "import com.google.gson.Gson;\n")
s = s.replace("import fi.dy.masa.malilib.util.JsonUtils;\n", "")
s = s.replace("public class Configs implements IConfigHandler\n{\n",
              "public class Configs implements IConfigHandler\n{\n"
              "    private static final Gson GSON = new Gson();\n")

old_load = """            JsonElement element = JsonUtils.parseJsonFileAsPath(configFile);

            if (element != null && element.isJsonObject())
            {
                JsonObject root = element.getAsJsonObject();
                ConfigUtils.readConfigBase(root, "Generic", Generic.OPTIONS);
                ConfigUtils.readConfigBase(root, "Hotkeys", Hotkeys.HOTKEY_LIST);
            }
"""
new_load = """            try (Reader reader = Files.newBufferedReader(configFile, StandardCharsets.UTF_8))
            {
                JsonElement element = JsonParser.parseReader(reader);
                if (element != null && element.isJsonObject())
                {
                    JsonObject root = element.getAsJsonObject();
                    ConfigUtils.readConfigBase(root, "Generic", Generic.OPTIONS);
                    ConfigUtils.readConfigBase(root, "Hotkeys", Hotkeys.HOTKEY_LIST);
                }
            }
            catch (Exception e)
            {
                LitematListMod.LOGGER.error("读取配置失败", e);
            }
"""
if old_load not in s:
    raise SystemExit("Expected Configs load block was not found")
s = s.replace(old_load, new_load, 1)

old_save = "        JsonUtils.writeJsonToFileAsPath(root, configFile);\n"
new_save = """        try (Writer writer = Files.newBufferedWriter(configFile, StandardCharsets.UTF_8))
        {
            GSON.toJson(root, writer);
        }
        catch (Exception e)
        {
            LitematListMod.LOGGER.error("保存配置失败", e);
        }
"""
if old_save not in s:
    raise SystemExit("Expected Configs save block was not found")
s = s.replace(old_save, new_save, 1)
p.write_text(s, encoding="utf-8")

bad = []
for p in root.rglob("*.java"):
    text = p.read_text(encoding="utf-8")
    for token in [
        "Minecraft.getInstance().setScreen(",
        "client.setScreen(",
        "GpuTextureView",
        "GpuSampler",
        "JsonUtils",
    ]:
        if token in text:
            bad.append(f"{p}: {token}")

if bad:
    raise SystemExit("Unpatched symbols:\n" + "\n".join(bad))

print(f"Patched {count} Java files for Minecraft 26.3")
