import os
from distutils.util import strtobool
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Union

from common_utils.constants import (
    PASSWORD_RESET_TOKEN_EXPIRATION_TIME,
    REGION,
    SURROUNDING_SOURCES,
)

CELERY_MAX_RETRIES = 5
CELERY_RETRYBACKOFF = True
CELERY_RETRY_DELAY_DMS_BACKUP = 300  # retry after 5 minutes

# Places for nightly execution of Surroundings QA analysis.
SURROUNDINGS_LOCATIONS_PERIODIC_QA = {
    "watery_OSM": (
        "010300000001000000090000008E9A12BF2BD62040AB7E7125B3834740C684B1EA2BD620400E44E29AB3834740C3BCE78037D620401F53AF7CB3834740E29EEBBB35D62040BED2E77AAE8347403B6510292AD62040ADC31A99AE834740D41420CA2AD62040B71EF663B083474092A0B5AC1FD6204013505281B08347409E2403A520D620400AB0CD42B38347408E9A12BF2BD62040AB7E7125B3834740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.OSM,
    ),  # lakes
    "watery_SWISSTOPO": (
        "010300000001000000150000005FC66ECA30D62040AFB88FE6AD8347402CCF321E2CD62040B71A0406AE834740439B3E4328D620401180E41FAE8347401627019723D620405086453FAE83474065C6507A25D620404D99F158B08347405F0ED1041BD620409828459FB08347403C3B694C1BD620408BB7F4EEB083474059C536161CD6204040117ACFB1834740A8F2ACB61CD62040639EC081B2834740D543157F1DD62040CD974B61B3834740E29DF3CB1DD620401174B4B6B3834740D2255B4128D62040C7015F70B38347403B82F7BD28D62040BD450EFBB38347402287346A2DD620402DE899DBB3834740C021B74431D62040656AA6C1B3834740E71065F135D62040F2C331A2B3834740D917AE4034D62040E1B8B4C0B183474007FBDD7F3BD620409497FB8FB18347408961EF6B39D62040FA73D63FAF8347406047862C32D62040DC159170AF8347405FC66ECA30D62040AFB88FE6AD834740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.SWISSTOPO,
    ),  # lakes
    "mountains_OSM": (
        "0103000000010000000500000075F103573EF81E4062528487E127474021A15DE012F81E40309BE675E127474013EE034612F81E4006B4A445E42747405D3EAABC3DF81E403A6B4257E427474075F103573EF81E4062528487E1274740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.OSM,
    ),
    "mountains_SWISSTOPO": (
        "0103000000010000000D000000998F781320F81E40082D8429E527474089A49E3820F81E400CAA79F9E52747404D03045220F81E40F5993885E6274740DB4391BB3DF81E409B3C8883E627474073E90FAD3DF81E400C1A90B5E4274740BA2A10AD3DF81E40091A90B5E4274740AD36EF7441F81E407D8250B5E42747405A1B735F41F81E400D3EA6D5E1274740D6E5E6A415F81E40EEDC2FD8E1274740D08B45AC15F81E40491C3EDFE2274740CB46641F02F81E40B45563E0E2274740141BD53002F81E402EAA3E2BE5274740998F781320F81E40082D8429E5274740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.SWISSTOPO,
    ),
    "railways_OSM": (
        "010300000001000000070000000FE36CBB88092140ABFDD25E50B14740A4889E70890921402DDCEEA150B14740FFD688E1A20921406F7A7FE44EB147407005427D94092140B258CAA448B147404A0E7A5C780921401FE5018D4AB14740539AC4467D092140419E151E51B147400FE36CBB88092140ABFDD25E50B14740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.OSM,
    ),
    "railways_SWISSTOPO": (
        "0103000000010000000E0000005D7494CB9409214067F358A048B14740E05A5B867F092140567C26114AB1474059585AE778092140CEC8F4834AB14740FF05E98D7A092140DBF668864CB14740A6F105597B0921403A325B7D4DB14740AEDCE9747D092140C42A730E50B14740C1BB664C7E092140EA90FC1451B14740ACF39E6E870921401873727950B147400B71FBF488092140BACB212F51B147406E0D6EA69F09214066A9C8A54FB14740EC71CF539A092140FC4008604DB14740C6077B399609214010821FB24BB14740F7D00A269B09214027A2145D4BB147405D7494CB9409214067F358A048B14740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.SWISSTOPO,
    ),
    "buildings_OSM": (
        "01030000000100000017000000D9AC4A92550A2140C710BE5890B147408DB53889650A2140EF92795694B14740CD5EF034620A2140F9219FB894B14740394F4957680A21400E5E354196B1474002F826076B0A214061055BF295B1474062DCB2589D0A2140F6BD9487A2B14740CC26B6E1D40A2140612A5A2B9CB14740D89E52DFB10A2140E088EA6993B14740E736BEB0B40A21405672DE1693B14740951759ECAE0A2140832AC5A591B147403B86810DAC0A2140AA00A8F991B14740272B49B38C0A2140FAE919238AB1474020D9B3578D0A21402F73A5108AB14740DD575D527E0A2140EAD24F4F86B1474012F066227F0A21400B1FFC3686B14740685A1848740A214011BA917F83B1474002A36CA6550A2140CA39FD0187B147401C974BBF570A2140D0F6348887B147400AA4BE9C470A214052CA296289B147402E2E288D500A2140476D6D9D8BB14740417550F9450A21406352CED38CB147401F313689540A214053C1C77790B14740D9AC4A92550A2140C710BE5890B14740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.OSM,
    ),
    "buildings_SWISSTOPO": (
        "0103000000010000003F0000001952998B500A214061C812998BB1474078B9FBF84B0A21406448F9218CB1474041E0477B460A21406AFD6FC68CB1474004ADA946490A2140A97F54798DB14740D8282911550A21400109396C90B1474067C2B2D0550A214059B0315690B147400E625F6E570A2140580F21BD90B14740DE942D605D0A2140AA6FE73792B147400422F558620A21408C0DA27493B147405BA1B586650A2140FBF4363F94B1474021D3E22F660A21400C4E266994B14740D6FF02EA640A2140779B218E94B14740353D107C630A21409F9BA8B794B147402823BCA7650A214079A92D4295B1474043C7D347690A214005529E2996B147404EC2629D6A0A21408975C00096B14740B527F0F26B0A21406D48CFD795B147408B8DCB6C6D0A21408C03003696B147406F085D28750A214076849A2398B147406778FAF67C0A2140D32ED7159AB14740DF69F68C7E0A2140F6CE0E7B9AB14740DFF9B3C4840A2140E3FF00089CB1474008B0A5CC8B0A214024E5C0C89DB14740C945396D8C0A21403E22BFF09DB14740F19903D18C0A21403B7F90099EB14740CEAA022C910A2140FCA6A61F9FB14740E293320D9F0A214035189095A2B1474051E63F59A40A2140722501F8A1B147409E52016FD00A21404BA3F8DA9CB14740191825EED50A2140F7A3C8379CB14740925929F0C70A2140B886B7BD98B14740376CBA2EC30A2140A2221F8F97B14740DEBE5A81BB0A2140D191EBA695B14740C363C8AEB30A214092A45FB593B1474052F6975AB20A2140064ED46093B14740B7CD8901B40A21402E6ABC2D93B1474015914FE3B40A21401D9C6B1293B147400F82D70FAF0A2140A1D140A491B14740F3D1658AAC0A2140E6F62EEF91B147404449C2DBAB0A2140A549ADC391B14740BB68561BA40A2140255B9DD68FB147405BFA5D349C0A214001EBFBDF8DB14740FFA5710D940A2140EA446ED98BB14740877A1C2D8D0A2140582722248AB1474006F84E7B8C0A2140CE7FF4F789B14740485AC50F8D0A2140A150D6E789B14740BBE109EC7E0A214095F03B6286B147406AFAE8A87E0A2140A486905186B147401FAE44DC620A21406A72528089B14740D065F41C5E0A2140AF01840B8AB14740E59ABB6C5C0A214012A78CA089B14740B612BFA95F0A214021BAFC3F89B147407ADDB36E5B0A214056F5023488B147407A75724C580A21405E91779188B1474092A98CE5540A2140F1E06CB787B1474028593558540A21401665ADC787B14740D944660E4C0A2140828B84BC88B147402936C1BD4F0A2140E6B6F5A589B147409D8C5A6A510A2140F4C61A108AB147400BD8DA45550A21405799FC9C89B1474030940843590A214089A8A8998AB147400F6AA4FD500A2140439CFA8B8BB147401952998B500A214061C812998BB14740",
        [3],
        REGION.CH,
        SURROUNDING_SOURCES.SWISSTOPO,
    ),
    "streets_OSM": (
        "0103000000010000002000000042A0EE634C9818409BB20E15001947400A0448943D98184094EAAF2501194740F8D5A5015E981840E95572D20719474040DA7EFE67981840104BE96707194740BAD1A7106A981840303B710707194740609DD27C709818409D1A87C80619474072171D9587981840B1FAF80808194740DC8299BB8298184045A02ABE0819474063D1212B9A981840DFFDA4030A194740B129717D9F9818404258734E09194740BC7900EBB898184033E749B10A194740D72014AAD1981840267B0F0A0C1947409E651F1FCF98184068CBB0690C1947405DE6221ED09818401A297AAE0C194740F8684424E59818404C1DA8C60D194740741DA5BCE7981840502297BC0D1947404CCB7162EA981840874FFE610D1947403F54EB5D03991840382248BD0E1947400D319FB11B991840E2D8274E0B194740B0E7A33602991840AB88D5ED09194740A3A58FB4F6981840D0174A4F091947400F8276E7D09818409CDCAD4407194740B2C8E94BB698184034D5BDD205194740EFE5F40BAC981840F45BF944051947400E86A7B786981840A7DE8E3E03194740A2D7870B769818409D9231560219474036760EC564981840C2CA70650119474050E9ADE16998184023ED4EA0001947403E141D845B9818400ECA14E6FF1847400ED08909569818403CF28C95FF1847406D4A351353981840A232B694FF18474042A0EE634C9818409BB20E1500194740",
        [2],
        REGION.CH,
        SURROUNDING_SOURCES.OSM,
    ),
    "streets_SWISSTOPO": (
        "0103000000010000001F000000B9B67020729818402FB5E615071947407D0DA84E8598184037AF4721081947404C372E5C80981840F0797CD008194740119FBA26999818407D83142A0A1947409EDBCB199E9818402C76D97A09194740C19D2FD5B5981840E68AA0C50A194740B2D1F5CDB6981840E428EDA40A1947403EEBE534BE98184005ED150C0B194740339BEF34BE9818400097140C0B194740FA47D36ED098184015F7110A0C1947404632EC74CC9818401EC51A970C194740E6F10A5EE4981840E6DC5FE40D194740075D9AEBED981840E1A913A50D1947407D15A1EA0299184074B9BBC90E1947404E45F2BD109918404A7EEDDF0C194740223653EB1A991840322A5A770B194740EA559D571C9918408A09EE440B1947409D5EDDA1D798184085204A8707194740268FE7A1D79818403DB9488707194740400AF83AD09818407502202007194740D1C533BED19818406E9CECEB06194740E698597287981840AA8361E00219474004996E7C85981840400BD6250319474085F55DAE64981840875D935C01194740B612870E67981840B6EA7508011947408C3BB46E579818407F10BF2E00194740D2FC9F0E55981840AC99D98200194740BE81C1444B9818406E6C72FAFF184740A6BFA5C03A981840F255D52D011947406D718E1B5C981840FFDF86E307194740B9B67020729818402FB5E61507194740",
        [2],
        REGION.CH,
        SURROUNDING_SOURCES.SWISSTOPO,
    ),
    "rivery_OSM": (
        "0103000000010000000600000001BFEEC475B02040D75CFB91E4AB47402AC818B981B02040E215DC9EE2AB4740E48E792372B020404D4E08ACDEAB47401990691862B02040F5530422E1AB4740A92A09EA6EB02040422D9370E3AB474001BFEEC475B02040D75CFB91E4AB4740",
        [4],
        REGION.CH,
        SURROUNDING_SOURCES.OSM,
    ),
    "rivery_SWISSTOPO": (
        "010300000001000000050000008677D01560B020403BC7BB3BE1AB4740251E799B72B020407672F361E4AB4740BE59BB7C7EB02040CE10885DE2AB47403B124F436EB02040BC4677D3DEAB47408677D01560B020403BC7BB3BE1AB4740",
        [4],
        REGION.CH,
        SURROUNDING_SOURCES.SWISSTOPO,
    ),
    "river_prague": (
        "0103000000020000001B0000004274238AADD42C40583EE05FB50949400642CDEEADD42C407ABD8D61B509494081E760A5B0D42C40A5EB3D84B3094940358D3059AFD42C402A451251B30949403B3AAAF8A3D42C4075E25916B3094940E2403EEBA3D42C40EA5A7325B309494098DA4DA98AD42C40B514B0B1B20949404191682767D42C404FF809EAB109494079E88A7764D42C40538C1E42B20949407B87C63863D42C40463F29DDB3094940FD134D2064D42C405C7C08E3B30949400052C4A261D42C40BB5F261EB70949405D9874145FD42C40C572FB79BA094940FF713F605DD42C403D1E16A3BA094940662392FC5BD42C404732837BBB094940CF49C7B05DD42C4031042258BC094940E2F5505B62D42C407E87C4D1BC0949402E55709D63D42C402C8969CEBC094940A95279AA71D42C4073E83911BF094940D7CE68BF88D42C406E5244BFC2094940E42ADC0688D42C400A451CDAC20949406416A83490D42C40D01C552BC409494033A4F91C97D42C40B98351DDC3094940C5536BBF99D42C404E2A1B0FC20949406098D83599D42C40C7AC120AC209494023ED0393A4D42C40C83422F6BA0949404274238AADD42C40583EE05FB5094940130000004FC104DD8CD42C40AB36B4F0B70949402E1FBB1F8AD42C40F61F0A9FB90949406329D50886D42C401261401EBC094940F62C5BFF81D42C4043B7CAF1BB0949408D91A5347FD42C400FAEE683BB094940254885C57BD42C4064FED6E2BA0949409A2BF2FF7DD42C405A93E5B8BA09494040E0F0967ED42C40DCECB985BA0949405F93E82F7DD42C4023CDC9C4B9094940BDB6ADE678D42C4095BBAC67B90949402E3956E279D42C40AFF3EB76B8094940208B4D3F7BD42C40BD3BF2E5B6094940A403B64D7AD42C40781474B4B609494076C71FC578D42C40999810ACB6094940ABA2F10E79D42C401FBFE35EB60949406715193186D42C40B9DFCD9DB6094940415BB3A98DD42C40E48C8DC3B60949401F29FB0C8CD42C40278B99C7B70949404FC104DD8CD42C40AB36B4F0B7094940",
        [0, 3],
        REGION.CZ,
        SURROUNDING_SOURCES.OSM,
    ),
    "mountain_prague": (
        "010300000001000000120000000C8F36A655CE2C407926B1AAC50A4940582C2F6C56CE2C407141EE72C20A4940E7FC0CD160CE2C40F7F6E687C20A4940E8E1800965CE2C402B293D23C20A49403B03C7C766CE2C4009F73587C10A49403A8957BB65CE2C40745BE2BDC00A494039A4E38261CE2C40F01BB33CC00A49403589919829CE2C4057CDB6D9BF0A4940FFA3E16229CE2C40000CECDCC00A4940F6D28B0327CE2C40194EBAD8C00A49409D17F97926CE2C40D22F8216C30A4940DD84569A1DCE2C40AA78E404C30A49403DDF24E51CCE2C406A5F9B38C50A4940A5736CC125CE2C40E9D7B447C50A4940683C273026CE2C404EDB4D40C40A4940044D5E2146CE2C40B5817973C40A4940766E42DE45CE2C4005B38691C50A49400C8F36A655CE2C407926B1AAC50A4940",
        [0, 3],
        REGION.CZ,
        SURROUNDING_SOURCES.OSM,
    ),
}

EMAIL_TEMPLATE_LOCATION = (
    Path(__file__).resolve().parent.parent.joinpath("email_templates")
)


class EmailTypes(Enum):
    ACTIVATION_EMAIL = auto()
    PASSWORD_RESET = auto()


EMAIL_TEMPLATE_BY_TYPE: Dict[EmailTypes, Path] = {
    EmailTypes.ACTIVATION_EMAIL: EMAIL_TEMPLATE_LOCATION.joinpath(
        "generic_email_template.html"
    ),
    EmailTypes.PASSWORD_RESET: EMAIL_TEMPLATE_LOCATION.joinpath(
        "generic_email_template.html"
    ),
}
EMAIL_CONTENT_BY_TYPE: Dict[EmailTypes, Dict[str, Union[Path, str]]] = {
    EmailTypes.ACTIVATION_EMAIL: {
        "subject": "Archilyse account activation request",
        "body_content": f"Please click the link below to activate your account. It's only "
        f"valid for {PASSWORD_RESET_TOKEN_EXPIRATION_TIME // 3600 } hour(s)",
        "call_to_action": "Activate account",
        "body_footer": "If you did not make this request, just ignore this email.<br>Otherwise please click the button above to activate your account.",
    },
    EmailTypes.PASSWORD_RESET: {
        "subject": "Archilyse password reset request",
        "body_content": "Please click the link below to reset your password, <br>"
        f"valid for {PASSWORD_RESET_TOKEN_EXPIRATION_TIME // 3600 } hour(s)",
        "call_to_action": "Reset password",
        "body_footer": "If you did not make this request, just ignore this email.<br>Otherwise please click the button above to reset your password.",
    },
}

sendgrid_sandbox_mode = bool(strtobool(os.environ.get("TEST_ENVIRONMENT", "False")))