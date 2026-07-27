package kenchiku;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KenchikuQuestMod implements ModInitializer {
    public static final String MOD_ID = "kenchikuquest";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        System.out.println("kenchiku-quest loaded");
        LOGGER.info("Kenchiku Quest initialized");
    }
}
