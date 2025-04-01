main()

Sub main
	Dim ie

	' IE起動
	Set ie = CreateObject("InternetExplorer.Application")
	Set subIE = CreateObject("InternetExplorer.Application")

	'ログイン	
	login(ie)

	'すべてのプレゼントのページへ遷移
	doAccess "https://furifuru.com/category/present/", ie
	lotteryForThisPage ie, subIE

	doAccess "https://furifuru.com/category/present/page/2/", ie
	lotteryForThisPage ie, subIE

	doAccess "https://furifuru.com/category/present/page/3/", ie
	lotteryForThisPage ie, subIE

	doAccess "https://furifuru.com/category/present/page/4/", ie
	lotteryForThisPage ie, subIE
	
	doAccess "https://furifuru.com/category/present/page/5/", ie
	lotteryForThisPage ie, subIE

	killIE ie
	killIE subIE

End Sub

Sub lotteryForThisPage(objIE, subObjIE)

	'リンク格納用オブジェクト
	Set arrItems = CreateObject("System.Collections.ArrayList")
	
	'重複削除
	For Each alink in objIE.Document.Links
		if Not arrItems.Contains(alink.href) Then
			arrItems.add alink.href
		End If
	Next 

	For Each objItem In arrItems

		'「POST」を含むページへ
		If InStr(objItem,"post") > 0 Then

			doAccess objItem, subObjIE

			' "entry"リンクを押す
			keywordAccess  subObjIE, "entry"
			
			' "応募する"ボタンを押す
			buttonClick subObjIE, "input", "応募する"

		End If

	'次のリンクへ
	Next

End Sub

Sub login(ie)
	WScript.echo "login"

	' ログイン画面へ
	doAccess "https://furifuru.com/supporter_login/",ie
	
	' ログイン情報入力
	With ie.document      
        	.getElementsByName("email")(0).Value = ""   
        	.getElementsByName("password")(0).Value = ""
	End With

	buttonClick ie, "input", "ログイン"

End Sub

Sub doAccess(pageURL, objIE)
	WScript.echo "doAccess" & ":" & pageURL
	objIE.Navigate pageURL
	objIE.Visible = True
	waitIE objIE

End Sub

Sub keywordAccess(objIE, keyword)
	WScript.echo "keywordAccess:" & keyword

	Dim result
	result = "Nothing"


	For Each objItem In objIE.Document.Links
		If InStr(objItem.href,keyword) > 0 Then
			'送信ボタンクリック
			result = "Find!" & objItem.href
			objIE.Navigate objItem.href
			waitIE objIE
			Exit For
		End If
	Next

	WScript.echo "■keywordAccess:" + result

	waitIE objIE
	
End Sub

Sub buttonClick(objIE, tagName, buttonTxt)
	WScript.echo "buttonClick:" & buttonTxt

	Dim result
	result = "Nothing"

	'ボタンクリック
	For Each objTag In objIE.document.getElementsByTagName(tagName)

		If InStr(objTag.outerHTML, buttonTxt) > 0 Then

			'送信ボタンクリック
			result = "Find!" & objTag.outerHTML
			objTag.Click

			'IEが完全表示されるまで待機
			waitIE objIE

			'ループ脱出
			Exit For

		End If

	Next

	WScript.echo "■buttonClick:" + result

	'IEが完全表示されるまで待機
	waitIE objIE

End Sub

' 制御を破棄
Sub killIE(objIE)
    objIE.Quit
    Set objIE = Nothing
End Sub

' IEがビジー状態の間待ちます
Sub waitIE(objIE)   
    Do While objIE.Busy = True Or objIE.readystate < 4
        WScript.Sleep 100
    Loop
        
End Sub