//---------------------------------------------------------------------------
//Salva o relatório de calibração no banco de dados
#pragma hdrstop

#include "ReportManagerSQL.h"
#include "ViewMain.h"
#include "StringUtils.h"
#include "LanguageManager.h"

#define     MATRIZ      (AnsiString)"01"
#define     AJUSTE      (AnsiString)"1"
#define     VALIDACAO   (AnsiString)"2"

#define     RECNO_ZZ8       (AnsiString)"SELECT MAX(R_E_C_N_O_) as Value FROM ZZ8010"
#define     RECNO_ZZ9       (AnsiString)"SELECT MAX(R_E_C_N_O_) as Value FROM ZZ9010"
#define     RECNO_READ_ZZ8  (AnsiString)"SELECT ZZ8_NUMEQ as Value FROM ZZ8010 WHERE R_E_C_N_O_ ='"
#define     RECNO_READ_ZZ9  (AnsiString)"SELECT ZZ9_SERIAL as Value FROM ZZ9010 WHERE R_E_C_N_O_ ='"
//---------------------------------------------------------------------------
#pragma package(smart_init)

ReportManagerSQL::ReportManagerSQL()
{
    try
	{
		stepList = new TList;
	}
	catch(...)
	{
		stepList = NULL;
	}
    this->SetRewrite(false);
}
//---------------------------------------------------------------------------
ReportManagerSQL::~ReportManagerSQL()
{
    if(stepList != NULL)
    {
        stepList->Clear();
        delete stepList;
        stepList = NULL;
    }
}
//---------------------------------------------------------------------------
void ReportManagerSQL::Add(StepAbstract *step)
{
    stepList->Add(step);
}
//---------------------------------------------------------------------------
void ReportManagerSQL::Remove(StepAbstract *step)
{
    if(step == NULL)
    {
        this->stepList->Clear();
    }
}
//---------------------------------------------------------------------------
void ReportManagerSQL::Update(StepAbstract *step)
{
}
//---------------------------------------------------------------------------
void ReportManagerSQL::SetDevice(Device *device)
{
    this->device = device;
}
//---------------------------------------------------------------------------
bool ReportManagerSQL::MakeReport(Device *device, int serialNumberIndex, bool bStatus, bool bSFirmware)
{
	TStringList *TsDate;
    AnsiString sQuery;
    AnsiString sQueryValid;
    AnsiString sValidSerialNumber;
    int iRecno;
    int iRetry = 0;
    bool bTest;

    try
    {
        //Modifica o separador de decimal para se adequar ao banco de dados
        if(DecimalSeparator != '.')
        {
            DecimalSeparator = '.';
        }

        //Resgata os valores para montar o cabeçalho do relatório
        sFilial                 = MATRIZ;
        sSoftwareVersion        = this->getSoftwareVersion();
        sJigaFirmwareVersion    = device->getDeviceFirmwareVersion();
        sJigaSerialNumber       = device->GetJigaSerialNumber();
        sProductName            = device->GetProduct();
        sProductFirmwareVersion = device->GetFirmwareVersion();
        sProductSerialNumber    = device->GetSerialNumber(serialNumberIndex);
        sProductMAC             = device->GetMacAddress();
        sOperatorName           = device->GetOperadorName();
        sRequestNumber          = device->GetNumPedido();
        sOPNumber               = device->GetCustomerName();
        sDate                   = device->GetDate();
        sTime                   = device->GetTime();
        sReview                 = device->GetReviewHardware();
        sProductMACLogBox       = device->GetMacAddressLogBox();
        sProductMACLogBoxWiFi   = device->GetMacAddressLogBoxWiFi();
        sProductIMEILogBox3G    = device->GetIMEILogBox3G();


        if(device->Get2StepCheck())
        {
            sTipo = VALIDACAO;
        }
        else
        {
            sTipo = AJUSTE;
        }
        TsDate = StringUtils::GetTextDelimited(sDate, '/');

        sDate = TsDate->Strings[2] + TsDate->Strings[1] + TsDate->Strings[0];
        if((bStatus == true) && (!device->GetValidCalibCheck()))
        {
            sStatusCalib = "A"; //Aprovado
        }
        else
        {
            sStatusCalib = "R"; //Reprovado
        }

        do
        {
            iRecno = 1 + StrToInt(MainForm->GetValueTable(RECNO_ZZ8));  //Retorna o valor de R_E_C_N_O_, chave primária da tabela ZZ8010
            sRecno = IntToStr(iRecno);
            //Monta a string com os valores
            sQuery = ("'"+ sFilial                 +  //ZZ8_FILIAL
                    "','"+ sSoftwareVersion        +  //ZZ8_SOFT
                    "','"+ sJigaFirmwareVersion    +  //ZZ8_FIRM
                    "','"+ sJigaSerialNumber       +  //ZZ8_NUMBER
                    "','"+ sProductName            +  //ZZ8_PNAME
                    "','"+ sProductFirmwareVersion +  //ZZ8_FIRMPR
                    "','"+ sProductSerialNumber    +  //ZZ8_NUMEQ
                    "','"+ sProductMAC             +  //ZZ8_MAC
                    "','"+ sOperatorName           +  //ZZ8_NAMEOP
                    "','"+ sRequestNumber          +  //ZZ8_ORDNUM
                    "','"+ sOPNumber               +  //ZZ8_OPNUM
                    "','"+ sDate                   +  //ZZ8_DATE
                    "','"+ sTime                   +  //ZZ8_HOUR
                    "','"+ sStatusCalib            +  //ZZ8_STATUS
                    "','"+ sTipo                   +  //ZZ8_TIPO
                    "','"+ sReview                 +  //ZZ8_REVISA 
                    "','"+ sProductMACLogBox       +  //ZZ8_MAC1                //LogBox-BLE
                    "','"+ sProductMACLogBoxWiFi   +  //ZZ8_MAC2                //LogBox-WiFi
                    "','"+ sProductIMEILogBox3G    +  //ZZ8_MEI
                    "','"+ sRecno                  +  //R_E_C_N_O_
                    "'");
        
            if(MainForm->SetReportInfo(sQuery))
            {
                //Valida a escrita no banco de dados
                sQueryValid = RECNO_READ_ZZ8 + sRecno + "'";
                sValidSerialNumber = MainForm->GetValueTable(sQueryValid);

                if(sValidSerialNumber == sProductSerialNumber)
                {
                    bTest = true;
                }
                else
                {
                    bTest = false;
                }
            }
            iRetry++;

        }while((iRetry < 3) && (bTest != true));

        if(!bTest)
        {
            if(DecimalSeparator != ',')
            {
                DecimalSeparator = ',';
            }
            return false;
        }

        if(bSFirmware)
        {
            //Varre as etapas
            for(int i = 0; i < stepList->Count; i++)
            {
                if(serialNumberIndex == ((StepAbstract*)this->stepList->Items[i])->GetStepDeviceOwner())
                {
                    //Acrescenta o resultado da etapa no relatório
                    sStepName   = (((StepAbstract*)stepList->Items[i])->GetName());
                    sOffset     = (((StepAbstract*)stepList->Items[i])->GetOffset());
                    sGain_1     = (((StepAbstract*)stepList->Items[i])->GetGain_1());
                    sGain_2     = (((StepAbstract*)stepList->Items[i])->GetGain_2());
                    sCntsLow    = (((StepAbstract*)stepList->Items[i])->GetCntsL());
                    sCntsHigh   = (((StepAbstract*)stepList->Items[i])->GetCntsH());
                    sRealValue  = (((StepAbstract*)stepList->Items[i])->GetRealValue());
                    sPercentErr = (((StepAbstract*)stepList->Items[i])->GetErrorPercent());
                    sStepStatus = (((StepAbstract*)stepList->Items[i])->GetSStatus());

                    iRetry = 0;

                    do
                    {
                        iRecno = 1 + StrToInt(MainForm->GetValueTable(RECNO_ZZ9));  //Retorna o valor de R_E_C_N_O_, chave primária da tabela ZZ9010
                        sRecno = IntToStr(iRecno);
                        //Monta a string com os valores
                        sQuery = ("'"+ sFilial              +  //ZZ9_FILIAL
                                "','"+ sStepName            +  //ZZ9_STEP
                                "','"+ sOffset              +  //ZZ9_OFFSET
                                "','"+ sGain_1              +  //ZZ9_GAIN1
                                "','"+ sGain_2              +  //ZZ9_GIAN2
                                "','"+ sCntsLow             +  //ZZ9_CONTB
                                "','"+ sCntsHigh            +  //ZZ9_CONTA
                                "','"+ sRealValue           +  //ZZ9_VALR
                                "','"+ sPercentErr          +  //ZZ9_ERRO
                                "','"+ sStepStatus          +  //ZZ9_STATUS
                                "','"+ sProductSerialNumber +  //ZZ9_SERIAL
                                "','"+ sDate                +  //ZZ9_DATE
                                "','"+ sTime                +  //ZZ9_HOUR
                                "','"+ sTipo                +  //ZZ9_TIPO
                                "','"+ sRecno               +  //R_E_C_N_O_
                                "'");

                        if(MainForm->SetReportStepInfo(sQuery))
                        {
                            //Valida a escrita no banco de dados
                            sQueryValid = RECNO_READ_ZZ9 + sRecno + "'";
                            sValidSerialNumber = MainForm->GetValueTable(sQueryValid);

                            if(sValidSerialNumber == sProductSerialNumber)
                            {
                                bTest = true;
                            }
                            else
                            {
                                bTest = false;
                            }
                        }
                        else
                        {
                            bTest = false;
                        }
                        iRetry++;

                    }while((iRetry < 3) && (bTest != true));

                    if(!bTest)
                    {
                        if(DecimalSeparator != ',')
                        {
                            DecimalSeparator = ',';
                        }
                        return false;
                    }
                }
            }
        }
        //retorna o separador decimal para ,
        if(DecimalSeparator != ',')
        {
            DecimalSeparator = ',';
        }
    }
    catch(...)
    {
        if(DecimalSeparator != ',')
        {
            DecimalSeparator = ',';
        }
        return false;
    }
    return true;
}
//---------------------------------------------------------------------------
void ReportManagerSQL::SetRewrite(bool bRewrite)
{
    this->bRewrite = bRewrite;
}
//---------------------------------------------------------------------------
// Lê a versão do programa da estrutura VERSIONINFO. O C++ Builder copia esta
// estrutura no executável do programa desde que a opção "include version
// information in project" tenha sido habilitada.
AnsiString ReportManagerSQL::getSoftwareVersion(void)
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
