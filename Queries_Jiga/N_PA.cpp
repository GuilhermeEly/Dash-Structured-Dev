//---------------------------------------------------------------------------
#include <vcl.h>
#pragma hdrstop

#include "Funcoes.h"

#include "ViewMain.h"
#include "ViewNewRegister.h"
#include "ViewAbout.h"
#include "SuportedDevices.h"
#include "ViewSteps.h"
#include "ViewSerialNumberMultiple.h"
#include "ViewSerialNumberMac.h"
#include "ViewSerialNumber.h"
#include "ViewReport.h"
#include "Login.h"
#include "ViewConnectionDeviceHID.h"
#include "ProductionOrder.h"

#include "CommunicationControlFactory.h"
#include "InterpreterFactory.h"
#include "EnumeratePortsComm.h"
#include "ConfigXmlReader.h"
#include "StepAbstract.h"
#include "JigaAPI.h"
#include "TaskInterface.h"
#include "LanguageManager.h"
#include "ParameterManager.h"
#include "GenericTypeDefs.h"
#include "StringUtils.h"
#include "Login.h"

#define GERAR_ARQUIVO_TRADUCAO      false
#define DEFAULT_LANGUAGE_FILE       (AnsiString)"Translate.trl"
#define DEFAULT_LANGUAGE_NAME       (AnsiString)"Português"
#define LANGUAGE_FILE_EXTENSION     (AnsiString)".trl"

//Parâmetros utilizados na escrita/leitura no Banco de Dados, correspondem aos valores das colunas nas tabelas do banco.
#define CAMPO_ZZ8010   (AnsiString)"ZZ8_FILIAL,ZZ8_SOFT,ZZ8_FIRM,ZZ8_NUMBER,ZZ8_PNAME,ZZ8_FIRMPR,ZZ8_NUMEQ,ZZ8_MAC,ZZ8_NAMEOP,ZZ8_ORDNUM,ZZ8_OPNUM,ZZ8_DATE,ZZ8_HOUR,ZZ8_STATUS,ZZ8_TIPO,ZZ8_REVISA,ZZ8_MAC1,ZZ8_MAC2,ZZ8_MEI,R_E_C_N_O_"
#define CAMPO_ZZ9010   (AnsiString)"ZZ9_FILIAL,ZZ9_STEP,ZZ9_OFFSET,ZZ9_GAIN,ZZ9_GAIN2,ZZ9_CONTB,ZZ9_CONTA,ZZ9_VALR,ZZ9_ERRO,ZZ9_STATUS,ZZ9_SERIAL,ZZ9_DATE,ZZ9_HOUR,ZZ9_TIPO,R_E_C_N_O_"
//---------------------------------------------------------------------------
#pragma link "CSPIN"
#pragma resource "*.dfm"

TMainForm *MainForm;
//---------------------------------------------------------------------------
__fastcall TMainForm::TMainForm(TComponent *Owner)
	: TForm(Owner)
{
}
//--------------------------------------------------------------------------- 
void __fastcall TMainForm::CreateMDIChild(String Name)
{
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::HelpAbout1Execute(TObject *Sender)
{
    AboutBox->SetVersion(this->sGetSoftwareVersion());
	AboutBox->ShowModal();
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::FileExit1Execute(TObject *Sender)
{
	Close();
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::FormShow(TObject *Sender)
{
//    #ifdef GERAR_ARQUIVO_TRADUCAO
//    Translate1->Visible = true;
//    #else
    Translate1->Visible = false;
//    #endif

    stlMessage = new TStringList;
    sLanguageFileName = ExtractFilePath(Application->ExeName) + "Translate" + LANGUAGE_FILE_EXTENSION;

    TranslateAll(sLanguageFileName);

    this->communicationControl = NULL;
    this->interpreterProtocol = NULL;
    this->hardwareDriverBridge = NULL;

    this->SetCaption();

    this->drawManager = new DrawManager();
    this->configFile = new ConfigFile("jiga[107].ini");
    LanguageManager::Init();
    ParameterManager::Init();
    timeDraw = new TTimer(this);
    timeDraw->Enabled = false;
    timeDraw->Interval = 20;
    timeDraw->OnTimer = TimerDraw;


    Application->OnMessage = AppMessage;
    Application->OnShortCut = this->AppMessageOnShortCut;
}
//---------------------------------------------------------------------------
void TMainForm::CreateJigaApi()
{
    if((this->configFile) == NULL && (this->jigaApi == NULL))
    {
        try
        {
            this->configFile = new ConfigFile("jiga[107].ini");
            this->jigaApi = new JigaAPI();
            this->jigaApi->SetConfigFile(this->configFile);
            this->jigaApi->SetProtocol(ConnectionForm->GetProtocol());
            // O número de relés da placa da jiga muda conforme a versão de firmware.
            this->jigaApi->relayAPI->SetNumberOfRelays();
        }
        catch(...)
        {
            this->configFile = NULL;
            this->jigaApi = NULL;
        }
    }
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::FormClose(TObject *Sender, TCloseAction &Action)
{
    if(memoUpdate != NULL)
    {
        delete memoUpdate;
        memoUpdate = NULL;
    }

    if(this->configFile != NULL)
    {
        delete this->configFile;
        this->configFile = NULL;
    }

    if(this->jigaApi != NULL)
    {
        delete this->jigaApi;
        this->jigaApi = NULL;
    }
    this->DeleteCommProtocol();

    for(int i = 0; i < MDIChildCount; i++)
    {
        MDIChildren[i]->Close();
    }

    if(this->drawManager != NULL)
    {
        delete this->drawManager;
        this->drawManager = NULL;
    }
}
//---------------------------------------------------------------------------
HardwareDriverObserver* TMainForm::GetMemoUpdate()
{
    return this->memoUpdate;
}
//---------------------------------------------------------------------------  
void __fastcall TMainForm::FormCreate(TObject *Sender)
{
    this->jigaApi = NULL;
    this->configFile = NULL;
    bProductionOrder = false;
    
    if(DecimalSeparator != ',')
    {
        DecimalSeparator = ',';
    }

    TIniFile *File = new TIniFile(ExtractFilePath(Application->ExeName) + "jiga.ini");
    SetUseDatabase(File->ReadString("Reports","database","0"));
    SetUseTxt(File->ReadString("Reports","TXT","1"));

    ADOConnection1->KeepConnection = GetUseDatabase();
}
//---------------------------------------------------------------------------
void TMainForm::SetUseDatabase(AnsiString sDatabase)
{
    bUseDatabase = StrToBool(sDatabase);
}
//---------------------------------------------------------------------------
void TMainForm::SetUseTxt(AnsiString sTXT)
{
    bUseTxt = StrToBool(sTXT);
}
//---------------------------------------------------------------------------
bool TMainForm::GetUseDatabase()
{
    return bUseDatabase;
}
//---------------------------------------------------------------------------
bool TMainForm::GetUseTxt()
{
    return bUseTxt;
}
//---------------------------------------------------------------------------
void TMainForm::SetCaption()
{
    this->Caption = AnsiString(stlMessage->Strings[25]) +
                    AnsiString(" v") +
                    this->sGetSoftwareVersion();
}
//---------------------------------------------------------------------------
void TMainForm::DeleteCommProtocol()
{
    if(this->communicationControl != NULL)
    {
        delete this->communicationControl;
        this->communicationControl = NULL;
    }

    if(this->interpreterProtocol != NULL)
    {
        delete this->interpreterProtocol;
        this->interpreterProtocol = NULL;
    }

    if(this->hardwareDriverBridge != NULL)
    {
        delete this->hardwareDriverBridge;
        this->hardwareDriverBridge = NULL;
    }
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::FileNewItemClick(TObject *Sender)
{
    LangUpdInit();
    LangUpdTranslateForm(frmLogin, sLanguageFileName.c_str());
    LangUpdTerminate();

    //Carrega o usuário do Windows
    this->sOperator = GetUser();
    frmLogin->setOperatorName(this->sOperator);

    //Carrega os logins para teste
    TIniFile *iniFile = new TIniFile(ExtractFilePath(Application->ExeName) + "jiga.ini");
    sParameterName = iniFile->ReadString("Configurations","OperatorsNames"," ");
    sFileProductException = iniFile->ReadString("Product","ProductList"," ");

    Operators = StringUtils::GetTextDelimited(sParameterName, ',');
    for(int i=0; i < Operators->Count; i++)
    {
        if(this->sOperator == Operators->Strings[i])
        {
            bProductionOrder = true;
        }
    }

    if(bProductionOrder)
    {
        // Carrego Operador
        AnsiString FilePath = iniFile->ReadString("Configurations","OperatorsList","Operador.txt");
        this->sOperator = frmLogin->ShowLoginForm(FilePath);
        if(this->sOperator == "")
        {
            return;
        }
        delete iniFile;
    }
    CalibForm = new TCalibForm(this);

    TranslateAll(sLanguageFileName);
    CalibForm->SetConfigFile(this->configFile);
    CalibForm->SetDrawManager(this->drawManager);
    CalibForm->setOperatorName(this->sOperator);
    this->SetCaption();
    WindowTileVertical1->Execute();
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::FormResize(TObject *Sender)
{
    WindowTileVertical1->Execute();
}
//---------------------------------------------------------------------------
void TMainForm::SetConfigFile(ConfigFile *configFile)
{
    this->configFile = configFile;
}
//---------------------------------------------------------------------------
char* TMainForm::GetUser()
{
    DWORD nUserName = sizeof(cUserName);
    if (!GetUserName(cUserName, &nUserName))
        strcpy(cUserName, "User unidentified");

    return cUserName;
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::AppMessage(tagMSG &Msg, bool &Handled)
{
    if((Msg.message == WM_FORM_CREATE) || (Msg.message == WM_FORM_SHOW_MODAL) ||
       (Msg.message == WM_FORM_SHOW)   || (Msg.message == WM_FORM_DELETE))
    {
        iFormFunction = Msg.lParam;
        iFormIndex = Msg.wParam;
        timeDraw->Enabled = true;
        Handled = true;
    }
    else
    {

    }
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::TimerDraw(TObject *Sender)
{
    timeDraw->Enabled = false;
    switch(iFormFunction)
    {
        case FORM_FUNCTION_CREATE: this->drawManager->CreateForm(iFormIndex);return;
        case FORM_FUNCTION_SHOW_MODAL: this->drawManager->ShowModalForm();return;
        case FORM_FUNCTION_SHOW: this->drawManager->ShowForm();return;
        case FORM_FUNCTION_DELETE: this->drawManager->DeleteForm();return;
    }
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::AppMessageOnShortCut(TWMKey &Msg, bool &Handled)
{
    if(this->MDIChildCount)
        ((TCalibForm *)this->ActiveMDIChild)->AppMessageOnShortCut(Msg, Handled);
}
//---------------------------------------------------------------------------
// Lê a versão do programa da estrutura VERSIONINFO. O C++ Builder copia esta
// estrutura no executável do programa desde que a opção "include version
// information in project" tenha sido habilitada.
AnsiString TMainForm::sGetSoftwareVersion(void)
{
DWORD dwTamInfo, dwWnd;
UINT  dwTamVer;
PVSFixedFileInfo ArqInfo;
void *pVerBuf;
AnsiString sArquivo, sVersao;

   sVersao   = "1.00";
   sArquivo  = Application->ExeName;
   dwTamInfo = GetFileVersionInfoSize(sArquivo.c_str(), &dwWnd);

   if (dwTamInfo != 0)
   {
      pVerBuf = new(void*[dwTamInfo]);
      if (GetFileVersionInfo(sArquivo.c_str(), dwWnd, dwTamInfo, pVerBuf))
         if (VerQueryValue(pVerBuf, "\\", (LPVOID*)&ArqInfo, &dwTamVer))
            sVersao = Format("%d.%d.%d.%.02d",ARRAYOFCONST((HIWORD(ArqInfo->dwFileVersionMS),LOWORD(ArqInfo->dwFileVersionMS),HIWORD(ArqInfo->dwFileVersionLS),LOWORD(ArqInfo->dwFileVersionLS))));
      delete[](pVerBuf);
   }
   return sVersao;
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::miSuportedDevicesClick(TObject *Sender)
{
    frmDevices->SetDeviceList(this->configFile->getDeviceStrList());
    frmDevices->ShowModal();
}
//---------------------------------------------------------------------------
//Gera o arquivo de tradução
void __fastcall TMainForm::Translate1Click(TObject *Sender)
{
    AnsiString sLanguageFileName;

    sLanguageFileName = ExtractFilePath(Application->ExeName) + DEFAULT_LANGUAGE_FILE;
    LangUpdInit(sLanguageFileName.c_str());
    LangUpdCreateFormSection(MainForm);
    LangUpdCreateFormSection(AboutBox);
    LangUpdCreateFormSection(ConnectionForm);
    LangUpdCreateFormSection(SerialNumberForm);
    LangUpdCreateFormSection(SerialNumberMacForm);
    LangUpdCreateFormSection(ReportForm);
    LangUpdCreateFormSection(frmDevices);
    LangUpdCreateFormSection(frmLogin);
    LangUpdCreateFormSection(ConnectionDeviceHIDForm);
    LangUpdCreateFormSection(SerialNumberMultipleForm);
    LangUpdTerminate();
    Application->MessageBox("Arquivo de idioma gerado com sucesso.", "Atenção", MB_OK|MB_ICONINFORMATION);
}
//---------------------------------------------------------------------------
//Traduz o software conforme o arquivo Translate.trl
bool __fastcall TMainForm::TranslateAll(AnsiString sLanguageFileName)
{
    char* acValueList;
    
    LangUpdInit();
    LangUpdTranslateForm(MainForm, sLanguageFileName.c_str());
    LangUpdTranslateForm(AboutBox, sLanguageFileName.c_str());
    LangUpdTranslateForm(ConnectionForm, sLanguageFileName.c_str());
    LangUpdTranslateForm(SerialNumberForm, sLanguageFileName.c_str());
    LangUpdTranslateForm(SerialNumberMacForm, sLanguageFileName.c_str());
    LangUpdTranslateForm(ReportForm, sLanguageFileName.c_str());
    LangUpdTranslateForm(frmDevices, sLanguageFileName.c_str());
    LangUpdTranslateForm(frmLogin, sLanguageFileName.c_str());
    LangUpdTranslateForm(ConnectionDeviceHIDForm, sLanguageFileName.c_str());
    LangUpdTranslateForm(SerialNumberMultipleForm, sLanguageFileName.c_str());
    LangUpdTranslateForm(fmProductionOrder, sLanguageFileName.c_str());
    LangUpdTranslateForm(ProductException, sLanguageFileName.c_str());

    acValueList = (char*) new char*[TSTRINGLIST_MAX_NR_CARACTERES];
    LangUpdTranslateStringList(acValueList, "stlMessage", sLanguageFileName.c_str());
    stlMessage->CommaText = (AnsiString)acValueList;
    delete []acValueList;
    LangUpdTerminate();
    return true;
}
//---------------------------------------------------------------------------
// Funções para ler e escrever no Banco de Dados


//Parâmetro: numero da Ordem de Produção (OP)
//Retorno: numero do Produto Acabado (PA)
AnsiString TMainForm::GetNumberPA(AnsiString sQuery)
{
    AnsiString sProduct;

    sProduct = "";

    ADOCommand1->CommandText = "SELECT Z2_PRODUTO as NrPA FROM SZ2010 WHERE D_E_L_E_T_ = '' AND Z2_OP ='" + sQuery +"'";
    ADODataSet1->Recordset   = ADOCommand1->Execute();
    sProduct = ADODataSet1->FieldByName("NrPA")->AsString;
    return sProduct;
}
//---------------------------------------------------------------------------
//Retorna o Menor número de série pertencente a OP
AnsiString TMainForm::GetMinSerialNumber()
{
    AnsiString sNMin;

    ADOCommand1->CommandText = "SELECT MIN(Z2_SERIE) as NrMin FROM SZ2010 WHERE D_E_L_E_T_ ='' AND Z2_OP ='" + fmProductionOrder->GetProductionOrder() + "'";
    ADODataSet1->Recordset   = ADOCommand1->Execute();
    sNMin = ADODataSet1->FieldByName("NrMin")->AsString;

    sNMin = sNMin.Trim();

    return sNMin;
}
//---------------------------------------------------------------------------
//Retorna o Maior número de série pertencente a OP
AnsiString TMainForm::GetMaxSerialNumber()
{
    AnsiString sNMax;

    ADOCommand1->CommandText = "SELECT MAX(Z2_SERIE) as NrMax FROM SZ2010 WHERE D_E_L_E_T_ ='' AND Z2_OP ='" + fmProductionOrder->GetProductionOrder() + "'";
    ADODataSet1->Recordset   = ADOCommand1->Execute();
    sNMax = ADODataSet1->FieldByName("NrMax")->AsString;

    sNMax = sNMax.Trim();

    return sNMax;
}
//---------------------------------------------------------------------------
//Escreve o cabeçalho do relatório no banco de dados
// O relatório será formado pelo cabeçalho e as etapas
// A união das partes é feita com os seguintes parâmetros:
//  numero de série, data, hora, tipo(AJUSTE ou VALIDAÇÃO)
bool TMainForm::SetReportInfo(AnsiString sValue)
{
    try
    {
        ADOSetReportInfo->CommandText = ("INSERT INTO ZZ8010 (" + CAMPO_ZZ8010 + ") VALUES (" + sValue + ")");
        ADOSetReportInfo->Execute();
        return true;
    }
    catch(...)
    {
        return false;
    }
}
//---------------------------------------------------------------------------
//Escreve as etapas do relatório no banco de dados
bool TMainForm::SetReportStepInfo(AnsiString sValue)
{
    try
    {
        ADOSetReportInfo->CommandText = ("INSERT INTO ZZ9010 (" + CAMPO_ZZ9010 + ") VALUES (" + sValue + ")");
        ADOSetReportInfo->Execute();
        return true;
    }
    catch(...)
    {
        return false;
    }
}
//---------------------------------------------------------------------------
//Parâmetro: numero da Ordem de Produção (OP)
//Retorno: número da revisão da OP
AnsiString TMainForm::GetReviewHardware(AnsiString sQuery)
{
    AnsiString sReviewH;

    sReviewH = "";

    ADOCommand1->CommandText = "SELECT C2_REVISAO as NrVH FROM SC2010 WHERE D_E_L_E_T_ = '' AND C2_NUM+C2_ITEM+C2_SEQUEN ='" + sQuery +"'";
    ADODataSet1->Recordset   = ADOCommand1->Execute();
    sReviewH = ADODataSet1->FieldByName("NrVH")->AsString;
    return sReviewH;
}
//---------------------------------------------------------------------------
//Parâmetro: número da OP e ponteiro para armazenar número de série das Jigas
bool TMainForm::GetNumberJiga(AnsiString sQuary, AnsiString *sNumberJiga)
{
    try
    {
        ADOCommand1->CommandText = "SELECT ZZ8_NUMBER as Number FROM ZZ8010 WHERE ZZ8_OPNUM ='" + sQuary + "' AND ZZ8_STATUS = 'A' AND ZZ8_TIPO = '1' GROUP BY ZZ8_NUMBER";
        ADODataSet1->Recordset   = ADOCommand1->Execute();
        ADODataSet1->First();
        for (int i = 0; i < ADODataSet1->RecordCount; i++)
        {
            sNumberJiga[i] = ADODataSet1->FieldByName("Number")->AsString;
            ADODataSet1->Next();
        }
        return true;
    }
    catch(...)
    {
        return false;
    }
}
//---------------------------------------------------------------------------
// Parâmetro: comando SQL para resgatar uma informação do banco de dados.
// No parâmetro deverá constar qual tabela e uma variável "Value" onde
// será armazenada a resposta. O formato do campo no banco de dados deve ser
// string.
//
//Retorno: "Value"
AnsiString TMainForm::GetValueTable(AnsiString sValue)
{
    try
    {
        AnsiString sReturn;

        ADOCommand1->CommandText = sValue;
        ADODataSet1->Recordset   = ADOCommand1->Execute();
        sReturn = ADODataSet1->FieldByName("Value")->AsString;
        sReturn = sReturn.Trim();

        return sReturn;
    }
    catch(...)
    {
        return NULL;
    }
}
//---------------------------------------------------------------------------
//Parâmetro de entrada: Número de série digitado + produto que necessita MAC || Return: True caso encontre algum Mac relacionado ao NS
bool TMainForm::GetSearchSerialNumberMAC(AnsiString sSerialNumber, int iProduct, AnsiString *sReturnMac)
{
AnsiString sNumMac;
    try
    {
        switch(iProduct)
        {
            case 500:
            case 512:
            case 768:
            {
                ADOCommand1->CommandText = "SELECT ZY0_MAC as NrMac FROM ZY0010 WHERE D_E_L_E_T_ ='' AND ZY0_SERIAL ='" + sSerialNumber + "'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sNumMac = ADODataSet1->FieldByName("NrMac")->AsString;
                if(sNumMac != "")
                {
                    *sReturnMac = sNumMac;
                    return true;
                }
                break;
            }
            case 105:
            {
                ADOCommand1->CommandText = "SELECT ZY1_MAC as NrMac FROM ZY1010 WHERE D_E_L_E_T_ ='' AND ZY1_SERIAL ='" + sSerialNumber + "'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sNumMac = ADODataSet1->FieldByName("NrMac")->AsString;
                if(sNumMac != "")
                {
                    *sReturnMac = sNumMac;
                    return true;
                }
                break;
            }
            case 103:
            case 104:
            {
                ADOCommand1->CommandText = "SELECT ZY2_MAC as NrMac FROM ZY2010 WHERE D_E_L_E_T_ ='' AND ZY2_SERIAL ='" + sSerialNumber + "'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sNumMac = ADODataSet1->FieldByName("NrMac")->AsString;
                if(sNumMac != "")
                {
                    *sReturnMac = sNumMac;
                    return true;
                }
            }
        }
    }
    catch(...)
    {
        return false;
    }
    return false;
}
//---------------------------------------------------------------------------
//Parâmetro de entrada: Número de série digitado + produto que necessita MAC || Parâmetro de saída: Mac livre (sReturnMac), Máximo Mac do banco (sReturnMaxMac) || Return True: Caso encontre algum Mac relacionado ao NS
bool TMainForm::GetFreeSerialNumberMAC(AnsiString sSerialNumber, int iProduct, AnsiString *sReturnMac, AnsiString *sReturnMaxMac)
{
AnsiString sNumMac;
AnsiString sMaxMac;
AnsiString sRecnoMacFree;
AnsiString sRecnoMaxMac;

    try
    {
        switch(iProduct)
        {
            case 500:
            case 512:
            case 768:
            {
                ADOCommand1->CommandText = "SELECT MIN(R_E_C_N_O_) as NrRecnoMacFree FROM ZY0010 WHERE D_E_L_E_T_ ='' AND ZY0_SERIAL =''";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sRecnoMacFree = ADODataSet1->FieldByName("NrRecnoMacFree")->AsString;
                ADOCommand1->CommandText = "SELECT ZY0_MAC as NrMac FROM ZY0010 WHERE D_E_L_E_T_ ='' AND R_E_C_N_O_ ='"+ sRecnoMacFree +"'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sNumMac = ADODataSet1->FieldByName("NrMac")->AsString;
                ADOCommand1->CommandText = "SELECT MAX(R_E_C_N_O_) as NrRecnoMaxMac FROM ZY0010 WHERE D_E_L_E_T_ ='' AND ZY0_SERIAL=''";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sRecnoMaxMac = ADODataSet1->FieldByName("NrRecnoMaxMac")->AsString;
                ADOCommand1->CommandText = "SELECT ZY0_MAC as NrMaxMac FROM ZY0010 WHERE D_E_L_E_T_ ='' AND R_E_C_N_O_ ='"+ sRecnoMaxMac +"'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sMaxMac = ADODataSet1->FieldByName("NrMaxMac")->AsString;
                if(sNumMac != "")
                {
                    *sReturnMac = sNumMac;
                    *sReturnMaxMac = sMaxMac;
                    ADOCommand1->CommandText = "UPDATE ZY0010 SET ZY0_SERIAL ='" + sSerialNumber + "' WHERE ZY0_MAC ='" + sNumMac + "'";
                    ADOCommand1->Execute();
                    return true;
                }
                return false;
                break;
            }
            case 105:
            {
                ADOCommand1->CommandText = "SELECT MIN(R_E_C_N_O_) as NrRecnoMacFree FROM ZY1010 WHERE D_E_L_E_T_ ='' AND ZY1_SERIAL =''";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sRecnoMacFree = ADODataSet1->FieldByName("NrRecnoMacFree")->AsString;
                ADOCommand1->CommandText = "SELECT ZY1_MAC as NrMac FROM ZY1010 WHERE D_E_L_E_T_ ='' AND R_E_C_N_O_ ='"+ sRecnoMacFree +"'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sNumMac = ADODataSet1->FieldByName("NrMac")->AsString;
                ADOCommand1->CommandText = "SELECT MAX(R_E_C_N_O_) as NrRecnoMaxMac FROM ZY1010 WHERE D_E_L_E_T_ ='' AND ZY1_SERIAL=''";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sRecnoMaxMac = ADODataSet1->FieldByName("NrRecnoMaxMac")->AsString;
                ADOCommand1->CommandText = "SELECT ZY1_MAC as NrMaxMac FROM ZY1010 WHERE D_E_L_E_T_ ='' AND R_E_C_N_O_ ='"+ sRecnoMaxMac +"'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sMaxMac = ADODataSet1->FieldByName("NrMaxMac")->AsString;
                if(sNumMac != "")
                {
                    *sReturnMac = sNumMac;
                    *sReturnMaxMac = sMaxMac;
                    ADOCommand1->CommandText = "UPDATE ZY1010 SET ZY1_SERIAL ='" + sSerialNumber + "' WHERE ZY1_MAC ='" + sNumMac + "'";
                    ADOCommand1->Execute();
                    return true;
                }
                return false;
                break;
            }
            case 103:
            case 104:
            {
                ADOCommand1->CommandText = "SELECT MIN(R_E_C_N_O_) as NrRecnoMacFree FROM ZY2010 WHERE D_E_L_E_T_ ='' AND ZY2_SERIAL =''";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sRecnoMacFree = ADODataSet1->FieldByName("NrRecnoMacFree")->AsString;
                ADOCommand1->CommandText = "SELECT ZY2_MAC as NrMac FROM ZY2010 WHERE D_E_L_E_T_ ='' AND R_E_C_N_O_ ='"+ sRecnoMacFree +"'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sNumMac = ADODataSet1->FieldByName("NrMac")->AsString;
                ADOCommand1->CommandText = "SELECT MAX(R_E_C_N_O_) as NrRecnoMaxMac FROM ZY2010 WHERE D_E_L_E_T_ ='' AND ZY2_SERIAL=''";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sRecnoMaxMac = ADODataSet1->FieldByName("NrRecnoMaxMac")->AsString;
                ADOCommand1->CommandText = "SELECT ZY1_MAC as NrMaxMac FROM ZY2010 WHERE D_E_L_E_T_ ='' AND R_E_C_N_O_ ='"+ sRecnoMaxMac +"'";
                ADODataSet1->Recordset   = ADOCommand1->Execute();
                sMaxMac = ADODataSet1->FieldByName("NrMaxMac")->AsString;
                if(sNumMac != "")
                {
                    *sReturnMac = sNumMac;
                    *sReturnMaxMac = sMaxMac;
                    ADOCommand1->CommandText = "UPDATE ZY2010 SET ZY2_SERIAL ='" + sSerialNumber + "' WHERE ZY2_MAC ='" + sNumMac + "'";
                    ADOCommand1->Execute();
                    return true;
                }
                return false;
            }
        }
    }
    catch(...)
    {
        return false;
    }
    return false;
}
