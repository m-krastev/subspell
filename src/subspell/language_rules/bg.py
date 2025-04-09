"""Bulgarian language rules for spell checking."""

SYSTEM_INSTRUCTION = """<function>
ALWAYS PRESERVE AND KEEP THE FOLLOWING TAGS : §LINEBREAK§;§SEP§;§TAG§ . DO NOT MODIFY THEM OR SWAP THEM!
</function>
<instruction>
Генерирай списък с всички правописни, пунктуационни и граматични грешки, които могат да се намерят в текста. Бъди изчерпателен. 

**Отговаряй само с коригирания текст.**

</instruction>
<common_rules>
7.1. Когато думата е подлог в изречението или пояснява подлога и се съгласува с него, тя се членува с пълен член (-ът или -ят). Може да се направи проверка, като членуваната дума или цялото словосъчетание се замени с той.

Точно в дванайсет часа джентълменът се отправи към големия салон.
(Точно в дванайсет часа той се отправи към големия салон.)

В прохладния планински град ще ви посрещне спокойният и уютен хотел „Ралица".
(В прохладния планински град ще ви посрещне той.)

► Подлогът може да не означава истинския вършител на действието. Щом обаче може да се замести с той, думата се членува с пълен член.

Портретът е бил поръчан на Леонардо да Винчи от съпруга на Лиза дел Джокондо.
(Той е бил поръчан на Леонардо да Винчи от съпруга на Лиза дел Джокондо.)

7.2. Думата се членува с пълен член, когато е свързана с някой от следните глаголи: съм (ще бъда – бъд. време; бях – мин. време), оказвам се, изглеждам, казвам се, наричам се, ставам (някакъв), оставам (някакъв), представлявам (може да се замести със съм).

Със своите над 5000 записа в радиотеатъра Андрей Чапразов е несъмненият създател на този жанр в България.
Юджийн Сърнън се оказва последният човек, стъпил на Луната.
Франция остава най-големият износител на електроенергия в Европа през 2021 г.

7.3. Думата се членува с пълен член, когато е в заглавие, текст към изображение и подобни, употребена е без глагол и пред нея няма предлог.

„Последният самурай", „Старецът и морето"
Моят дядо, сниман в Пловдив

► Но: „Приключенията на добрия войник Швейк"

(За употребата на пълен член вижте по-подробно в тази статия.)

7.4. Когато думата не е подлог в изречението, нито пояснява подлога, тя се членува с кратък член (-а или -я). Може да се направи проверка, като членуваната дума или цялото словосъчетание се замени с него/го (в някои случаи – с тогава, там).

За три години обиколих целия континент.
(За три години го обиколих.)

Няколко пъти получателката не беше открита на адреса.
(Няколко пъти получателката не беше открита там.)

► Ако пред думата има предлог (на, в, с, за, от, при и др.), тя със сигурност не е подлог, нито определение към подлога, затова се членува с кратък член.

Бъди спокоен, няма да се поддам на външния натиск.
(При проверка: Бъди спокоен, няма да се поддам на него.)

7.5. Само с кратък член се членуват прякорите и прозвищата – дори и когато са подлог в изречението.

В подкаста ни днес се включва Камен Алипиев – Кедъра, един от известните спортни журналисти в България.

(За употребата на кратък член вижте по-подробно в тази статия.)

7.6. Членува се първата дума в собствени имена, които означават институции, организации и подобни на тях.

Управителят на Българската народна банка заяви, че присъединяването ни към еврозоната е политически въпрос. (а не: на Българска народна банка)
Цяло лято артистите от Софийската опера и балет ще изнасят представления. (а не: от Софийска опера и балет)

7.7. Когато две или повече определения се отнасят за два или повече обекта или групи обекти, се членуват всички определения.

Извършени са 2320 проверки на територията на Северното и Южното Черноморие. (два обекта: Северното Черноморие и Южното Черноморие)

Румънските леки коли, прибиращи се от българските и гръцките курорти, затрудняват движението в Русе. (две групи обекти: български курорти и гръцки курорти)

7.8. Бройната форма е специална форма за мн.ч. с окончание -а или -я. Тя се употребява, когато съществителното име не означава хора и е употребено след числително бройно име (четири, седемнайсет, 489) или след думите колко, няколко, колкото, толкова.

четири автомобила (а не: четири автомобили)
седемнайсет нарциса (а не: седемнайсет нарциси)
сто-двеста гвоздея (а не: сто-двеста гвоздеи)
колко екземпляра (а не: колко екземпляри)
няколко разказа (а не: няколко разкази)

► Бройната форма се употребява и когато между числителното име (също и колко, няколко, колкото, толкова) и съществителното име стои определение.

Потеглих към новия си живот с два огромни сиви куфара.

7.9. При съществителните имена, които означават хора, се употребява само обикновената форма за мн.ч., включително след числително бройно име (четирима, седемнайсет, 489) и думите колко, няколко, колкото, толкова.

четирима пианисти (а не: четирима пианиста)
седемнайсет санитари (а не: седемнайсет санитаря)
сто-двеста участници (а не: сто-двеста участника)
колко пенсионери (а не: колко пенсионера)
няколко поддръжници (а не: няколко поддръжника)

7.10. След думите десетки, стотици, милиони, милиарди (с които не се посочва точно количество), както и след думите двойка, тройка, десетка, дузина, чифт (съществителни имена) се употребява обикновената форма за мн.ч.

Десетки гълъби полетяха в небето на Бургас като символ на правото на достоен живот. (а не: десетки гълъба).
Токовите удари в малките населени места продължават да причиняват щети за хиляди левове. (а не: хиляди лева)

2.1. Слято се пишат прилагателните имена, които са образувани от съчетание на прилагателно и съществително име. 

етеричномаслен – от етерично масло
млечнокисел – от млечна киселина
граничнополицейски – от гранична полиция
източноазиатски – от Източна Азия

2.2. Слято се пишат думите със следните често срещани първи части, повечето от чужд произход: авто, анти, аудио, био, вице, евро, еко, електро, кибер, кино, макро, мега, микро, мини, мото, мулти, нарко, нео, под, полу, пост, пра, прес, промо, радио, свръх, смарт, соц, спец, супер, съ, термо, транс, ултра, фото, хидро, хипер и др.

автоуслуги, антибактериален, аудиосистема, биоферма, вицепрезидент, евродепутат, екотуризъм, електротабло, киберзащита, киноиндустрия, макрониво, мегапопулярен, микрокредит, минибар, мотописта, мултикултурен, наркокомуна, неонацист, подзаконов, полужив, постдигитален, прадядо, прессъобщение, промоцена, радиочестота, свръхпечалба, смартчасовник, соцмузей, спецполицай, супермощен, съфинансиране, термочаша, трансконтинентален, ултралек, фотостудио, хидротехника, хиперпродукция

► Но: евро-атлантически (Думата е образувана от равноправни части – евро(пейски) и атлантически, вж. т. 2.4.)

2.3. Слято се пишат прилагателните имена, чиято първа част е наречие и пояснява втората част – прилагателно име или причастие (глаголна форма, която завършва на -щ, -н или -м). Необходимо условие е двете части да образуват смислово единство.

взаимноприемлив, крайнодесен, общодостъпен, светлосин, яркочервен, властимащ, генномодифициран, високопроходим

► Такива прилагателни често имат първа част високо, вътрешно, горе, долу, ниско, ново, средно.

високоинтелигентен, вътрешнобанков, гореизброен, долупосочен, нискорисков, новопостъпил, средноаритметичен

 2.4. Полуслято се пишат съществителните и прилагателните имена, както и наречията, чиито части са в смислово равноправни отношения помежду си (между тях най-често може да се вмъкне и: старт-финал – старт и финал; черно-бял – черен и бял).

внос-износ; административно-битов, мускулно-скелетен, финансово-икономически; напред-назад, едва-едва

2.5. Полуслято се пишат думите, съдържащи число, когато представляват комбинация от цифри и букви.

5-годишен, 6-месечен, 3-стаен

► Но: петгодишен, шестмесечен, тристаен (Думите са написани само с букви.)

2.6. Полуслято се пишат степенуваните прилагателни имена, причастия и наречия.

по-красива, по-щадящ, по-кратко
най-умен, най-четена, най-често

2.7. Разделно се пишат съчетанията от две съществителни имена, ако второто пояснява първото и първото може да се членува: кокошка носачка – кокошката носачка.

лекар анестезиолог, художник символист, фирма посредник

► Но: кандидат-кмет, заместник-директор (Пишат се полуслято, защото се членува втората част: кандидат-кметът, заместник-директорът.)

 2.8. И разделно, и слято се пишат съществителните имена с една или две чужди съставни части, които отговарят на следните условия: а) първата част пояснява втората; б) двете части са свързани без съединителна гласна (о или е); в) двете части се употребяват като самостоятелни думи в българския език.

гел лак и геллак; рок концерт и рокконцерт; фен клуб и фенклуб; фитнес зала и фитнесзала

► Но: скречпостер, толтакса, тестдрайв (Думите не отговарят на условие в – първата или втората им част не се употребява като самостоятелна дума, затова се пишат само слято.)

2.9. Частицата не се пише разделно, когато стои пред глагол или деепричастие (глаголна форма, завършваща на -йки).

не знам, не сме, не искат
не знаейки, не искайки

2.10. Частицата не се пише слято с прилагателните имена и с причастията, които се употребяват като прилагателни.

неправилно (изпреварване), нечетлив (почерк), необикновена (ваканция), неизненадващо (изказване), непроверен (сигнал)

За всички неразбрали ще прочета текста отново.
► Но: Участниците не разбрали кога започва състезанието. (Употребено е като глагол.)
</common_rules>""" 