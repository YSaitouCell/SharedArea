main()

Sub main
	Dim ie

	' IE�N��
	Set ie = CreateObject("InternetExplorer.Application")
	Set subIE = CreateObject("InternetExplorer.Application")

	'���O�C��	
	login(ie)

	'���ׂẴv���[���g�̃y�[�W�֑J��
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

	'�����N�i�[�p�I�u�W�F�N�g
	Set arrItems = CreateObject("System.Collections.ArrayList")
	
	'�d���폜
	For Each alink in objIE.Document.Links
		if Not arrItems.Contains(alink.href) Then
			arrItems.add alink.href
		End If
	Next 

	For Each objItem In arrItems

		'�uPOST�v���܂ރy�[�W��
		If InStr(objItem,"post") > 0 Then

			doAccess objItem, subObjIE

			' "entry"�����N������
			keywordAccess  subObjIE, "entry"
			
			' "���傷��"�{�^��������
			buttonClick subObjIE, "input", "���傷��"

		End If

	'���̃����N��
	Next

End Sub

Sub login(ie)
	WScript.echo "login"

	' ���O�C����ʂ�
	doAccess "https://furifuru.com/supporter_login/",ie
	
	' ���O�C��������
	With ie.document      
        	.getElementsByName("email")(0).Value = ""   
        	.getElementsByName("password")(0).Value = ""
	End With

	buttonClick ie, "input", "���O�C��"

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
			'���M�{�^���N���b�N
			result = "Find!" & objItem.href
			objIE.Navigate objItem.href
			waitIE objIE
			Exit For
		End If
	Next

	WScript.echo "��keywordAccess:" + result

	waitIE objIE
	
End Sub

Sub buttonClick(objIE, tagName, buttonTxt)
	WScript.echo "buttonClick:" & buttonTxt

	Dim result
	result = "Nothing"

	'�{�^���N���b�N
	For Each objTag In objIE.document.getElementsByTagName(tagName)

		If InStr(objTag.outerHTML, buttonTxt) > 0 Then

			'���M�{�^���N���b�N
			result = "Find!" & objTag.outerHTML
			objTag.Click

			'IE�����S�\�������܂őҋ@
			waitIE objIE

			'���[�v�E�o
			Exit For

		End If

	Next

	WScript.echo "��buttonClick:" + result

	'IE�����S�\�������܂őҋ@
	waitIE objIE

End Sub

' �����j��
Sub killIE(objIE)
    objIE.Quit
    Set objIE = Nothing
End Sub

' IE���r�W�[��Ԃ̊ԑ҂��܂�
Sub waitIE(objIE)   
    Do While objIE.Busy = True Or objIE.readystate < 4
        WScript.Sleep 100
    Loop
        
End Sub